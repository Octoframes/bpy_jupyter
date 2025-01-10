"""Contains tools and procedures that deterministically and reliably packages the Blender extension.

This involves parsing and validating the plugin configuration from `pyproject.toml`, generating the extension manifest, downloading the correct platform-specific binary wheels for distribution, and zipping it all up together.
"""

import itertools
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from pathlib import Path

import rich
import rich.progress
import rich.prompt

from blext import paths, spec

####################
# - Resources
####################
console = rich.console.Console()


####################
# - Wheel Downloader
####################
def download_wheels(
	blext_spec: spec.BLExtSpec,
	*,
	os: str,
	delete_existing_wheels: bool = True,
) -> None:
	"""Download universal and binary wheels for all platforms defined in `pyproject.toml`.

	Each blender-supported platform requires specifying a valid list of PyPi platform constraints.
	These will be used as an allow-list when deciding which binary wheels may be selected for ex. 'mac'.

	It is recommended to start with the most compatible platform tags, then work one's way up to the newest.
	Depending on how old the compatibility should stretch, one may have to omit / manually compile some wheels.

	There is no exhaustive list of valid platform tags - though this should get you started:
	- https://stackoverflow.com/questions/49672621/what-are-the-valid-values-for-platform-abi-and-implementation-for-pip-do
	- Examine https://pypi.org/project/pillow/#files for some widely-supported tags.

	Args:
		delete_existing_wheels: Whether to delete all wheels already in the directory.
			This doesn't generally require re-downloading; the pip-cache will generally be hit first.
	"""
	# Delete Existing Wheels
	## TODO: Only replace wheels that need replacing.
	wheels = list(paths.PATH_WHEELS.rglob('*.whl'))
	if (
		len(wheels) > 0
		and delete_existing_wheels
		and rich.prompt.Confirm.ask(f'OK to delete "*.whl" in {paths.PATH_WHEELS}?')
	):
		console.log(f'[bold] Deleting Existing Wheels in {paths.PATH_WHEELS}')
		for existing_wheel in paths.PATH_WHEELS.rglob('*.whl'):
			existing_wheel.unlink()

	# Export 'requirements.lock' w/'uv export'
	with tempfile.NamedTemporaryFile(delete=False) as f_reqlock:
		reqlock_str = subprocess.check_output(['uv', 'export', '--no-dev', '--locked'])
		f_reqlock.write(reqlock_str)
		reqlock_path = Path(f_reqlock.name)
		## TODO: Use-after-close may not work on Windows.

	# Download Wheels
	if os in blext_spec.platforms:
		console.rule(f'[bold] Downloading Wheels for "{os}"')

		# Prepare Command
		platform_constraints = list(
			itertools.chain.from_iterable(
				[
					['--platform', pypi_platform_tag]
					for pypi_platform_tag in blext_spec.supported_oses[os]
				]
			)
		)
		cmd = [
			sys.executable,
			'-m',
			'pip',
			'download',
			'--requirement',
			str(reqlock_path),
			'--dest',
			str(paths.PATH_WHEELS),
			'--require-hashes',
			'--only-binary',
			':all:',
			'--python-version',
			blext_spec.req_python_version,
			*platform_constraints,
		]

		# Run Download
		progress = rich.progress.Progress()
		progress_task_id = progress.add_task(' '.join(cmd))
		with (
			rich.progress.Live(progress, console=console, transient=False) as live,
			subprocess.Popen(cmd, stdout=subprocess.PIPE) as process,
		):
			for line in process.stdout if process.stdout is not None else []:
				progress.update(progress_task_id, description=line.decode())
				live.refresh()

	# Cleanup the Temporary File
	reqlock_path.unlink()


####################
# - Pack Extension to ZIP
####################
def pack_bl_extension(
	blext_spec: spec.BLExtSpec,
	*,
	overwrite: bool = False,
) -> None:
	"""Pack all files needed by a Blender extension, into an installable `.zip`.

	Configuration data is sourced from `paths`, which in turns sources much of its user-facing configuration from `pyproject.toml`.

	Parameters:
		profile: Selects a predefined set of initial extension settings from a `[tool.bl_ext.profiles]` table in `pyproject.toml`.
		os: The operating system to pack the extension for.
		overwrite: Replace the zip file if it already exists.
	"""

	# Delete Existing ZIP (maybe)
	path_zip = paths.PATH_BUILD / blext_spec.zip_filename()

	# Overwrite
	if path_zip.is_file():
		if not overwrite:
			msg = f"File already exists where extension ZIP would be generated  at '{path_zip}'"
			raise ValueError(msg)
		path_zip.unlink()

	# Create New ZIP file of the addon directory
	console.rule(f'[bold] Creating zipfile @ {path_zip}')
	with zipfile.ZipFile(path_zip, 'w', zipfile.ZIP_DEFLATED) as f_zip:
		# Write Blender Extension Manifest @ /blender_manifest.toml
		with console.status('Writing Extension Manifest...'):
			f_zip.writestr(
				blext_spec.manifest_filename,
				blext_spec.manifest_str,
			)
		console.log('Wrote Extension Manifest.')

		# Write Init Settings @ /init_settings.toml
		with console.status('Writing Init Settings...'):
			f_zip.writestr(
				blext_spec.init_settings_filename,
				blext_spec.init_settings_str,
			)
		console.log('Wrote Init Settings.')

		# Install Addon Files @ /*
		with console.status('Writing Addon Files...'):
			for file_to_zip in blext_spec.path_pkg.rglob('*'):
				f_zip.write(
					file_to_zip,
					file_to_zip.relative_to(blext_spec.path_pkg),
				)
		console.log('Wrote Addon Files.')

		# Install Wheels @ /wheels/*
		## Setup UI
		total_wheel_size = sum(
			f.stat().st_size for f in paths.PATH_WHEELS.rglob('*') if f.is_file()
		)
		progress = rich.progress.Progress(
			rich.progress.TextColumn(
				'Writing Wheel: {task.description}...',
				table_column=rich.progress.Column(ratio=2),
			),
			rich.progress.BarColumn(
				bar_width=None,
				table_column=rich.progress.Column(ratio=2),
			),
			expand=True,
		)
		progress_task = progress.add_task('Writing Wheels...', total=total_wheel_size)

		## Write Wheels
		with rich.progress.Live(progress, console=console, transient=True) as live:
			for wheel_to_zip in blext_spec.wheels_path.rglob('*.whl'):
				f_zip.write(wheel_to_zip, Path('wheels') / wheel_to_zip.name)
				progress.update(
					progress_task,
					description=wheel_to_zip.name,
					advance=wheel_to_zip.stat().st_size,
				)
				live.refresh()

		console.log('Wrote Wheels.')

	console.rule(f'[bold green] Extension Packed to {blext_spec.zip_filename()}!')
	console.log(f'File was written to: {path_zip.parent}')
