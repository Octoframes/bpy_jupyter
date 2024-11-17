# oscillode
# Copyright (C) 2024 oscillode Project Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Contains tools and procedures that deterministically and reliably package the Blender extension.

This involves parsing and validating the plugin configuration from `pyproject.toml`, generating the extension manifest, downloading the correct platform-specific binary wheels for distribution, and zipping it all up together.
"""

import itertools
import json
import logging
import subprocess
import sys
import tempfile
import typing as typ
import zipfile
from pathlib import Path

import rich
import rich.progress
import rich.prompt
import tomli_w

from scripts import info

LogLevel: typ.TypeAlias = int

BL_EXT__MANIFEST_FILENAME = 'blender_manifest.toml'
BL_EXT__SCHEMA_VERSION = '1.0.0'
BL_EXT__TYPE = 'add-on'

####################
# - Generate Manifest
####################
# See https://docs.blender.org/manual/en/4.2/extensions/getting_started.html
# See https://packaging.python.org/en/latest/guides/writing-pyproject-toml
_FIRST_MAINTAINER = info.PROJ_SPEC['project']['maintainers'][0]
_SPDX_LICENSE_NAME = info.PROJ_SPEC['project']['license']['text']

## TODO: pydantic model w/validation
BL_EXT_MANIFEST = {
	'schema_version': BL_EXT__SCHEMA_VERSION,
	# Basics
	'id': info.PROJ_SPEC['project']['name'],
	'name': info.PROJ_SPEC['tool']['bl_ext']['pretty_name'],
	'version': info.PROJ_SPEC['project']['version'],
	'tagline': info.PROJ_SPEC['project']['description'],
	'maintainer': f'{_FIRST_MAINTAINER["name"]} <{_FIRST_MAINTAINER["email"]}>',
	# Blender Compatibility
	'type': BL_EXT__TYPE,
	'blender_version_min': info.PROJ_SPEC['tool']['bl_ext']['blender_version_min'],
	'blender_version_max': info.PROJ_SPEC['tool']['bl_ext']['blender_version_max'],
	'platforms': list(info.PROJ_SPEC['tool']['bl_ext']['platforms'].keys()),
	# OS/Arch Compatibility
	## See https://docs.blender.org/manual/en/dev/extensions/python_wheels.html
	'wheels': [
		f'./wheels/{wheel_path.name}' for wheel_path in info.PATH_WHEELS.iterdir()
	],
	# Permissions
	## * "files" (for access of any filesystem operations)
	## * "network" (for internet access)
	## * "clipboard" (to read and/or write the system clipboard)
	## * "camera" (to capture photos and videos)
	## * "microphone" (to capture audio)
	'permissions': info.PROJ_SPEC['tool']['bl_ext']['permissions'],
	# Addon Tags
	'tags': info.PROJ_SPEC['tool']['bl_ext']['bl_tags'],
	'license': [f'SPDX:{_SPDX_LICENSE_NAME}'],
	'copyright': info.PROJ_SPEC['tool']['bl_ext']['copyright'],
	'website': info.PROJ_SPEC['project']['urls']['Homepage'],
}


####################
# - Generate Init Settings
####################
## TODO: Use an enum for 'profile'.
def generate_init_settings_dict(profile: str) -> info.InitSettings:
	"""Generate initialization settings from a particular `profile` configured in `pyproject.toml`.

	Args:
		profile: The string identifier corresponding to an entry in `pyproject.toml`.

	Returns:
		The `info.InitSettings` structure to be bundled into the addon.
	"""
	profile_settings = info.PROJ_SPEC['tool']['bl_ext']['profiles'][profile]

	base_path = info.PATH_LOCAL if profile_settings['use_path_local'] else Path('USER')

	log_levels = {
		None: logging.NOTSET,
		'debug': logging.DEBUG,
		'info': logging.INFO,
		'warning': logging.WARNING,
		'error': logging.ERROR,
		'critical': logging.CRITICAL,
	}

	return info.InitSettings(
		use_log_file=profile_settings['use_log_file'],
		log_file_path=base_path
		/ info.normalize_path(profile_settings['log_file_path']),
		log_file_level=log_levels[profile_settings['log_file_level']],
		use_log_console=profile_settings['use_log_console'],
		log_console_level=log_levels[profile_settings['log_console_level']],
	)


####################
# - Wheel Downloader
####################
def download_wheels(delete_existing_wheels: bool = True) -> None:
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
	if delete_existing_wheels and rich.prompt.Confirm.ask(
		f'OK to delete "*.whl" in {info.PATH_WHEELS}?'
	):
		info.console.log(f'[bold] Deleting Existing Wheels in {info.PATH_WHEELS}')
		for existing_wheel in info.PATH_WHEELS.rglob('*.whl'):
			existing_wheel.unlink()

	with tempfile.NamedTemporaryFile(delete=False) as f_reqlock:
		reqlock_str = subprocess.check_output(['uv', 'export', '--no-dev', '--locked'])
		f_reqlock.write(reqlock_str)
		reqlock_path = Path(f_reqlock.name)
		## TODO: Use-after-close may not work on Windows.

	for platform, pypi_platform_tags in info.PROJ_SPEC['tool']['bl_ext'][
		'platforms'
	].items():
		info.console.rule(f'[bold] Downloading Wheels for {platform}')

		platform_constraints = list(
			itertools.chain.from_iterable(
				[
					['--platform', pypi_platform_tag]
					for pypi_platform_tag in pypi_platform_tags
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
			str(info.PATH_WHEELS),
			'--require-hashes',
			'--only-binary',
			':all:',
			'--python-version',
			info.REQ_PYTHON_VERSION,
			*platform_constraints,
		]

		progress = rich.progress.Progress()
		progress_task_id = progress.add_task(' '.join(cmd))
		with (
			rich.progress.Live(progress, console=info.console, transient=False) as live,
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
	profile: str,
	replace_if_exists: bool = False,
) -> None:
	"""Package a Blender extension, using a particular given `profile` of init settings.

	Configuration data is sourced from `info`, which in turns sources much of its user-facing configuration from `pyproject.toml`.

	Parameters:
		profile: Identifier matching `pyproject.toml`, which select a predefined set of init settings.
		replace_if_exists: Replace the zip file if it already exists.
	"""
	# Delete Existing ZIP (maybe)
	if info.PATH_ZIP.is_file():
		if replace_if_exists:
			msg = 'File already exists where extension ZIP would be generated ({info.PATH_ZIP})'
			raise ValueError(msg)
		info.PATH_ZIP.unlink()

	init_settings: info.InitSettings = generate_init_settings_dict(profile)

	# Create New ZIP file of the addon directory
	info.console.rule(f'[bold] Creating zipfile @ {info.PATH_ZIP}')
	with zipfile.ZipFile(info.PATH_ZIP, 'w', zipfile.ZIP_DEFLATED) as f_zip:
		# Write Blender Extension Manifest
		with info.console.status('Writing Extension Manifest...'):
			f_zip.writestr(BL_EXT__MANIFEST_FILENAME, tomli_w.dumps(BL_EXT_MANIFEST))
		info.console.log('Wrote Extension Manifest.')

		# Write Init Settings
		with info.console.status('Writing Init Settings...'):
			f_zip.writestr(
				info.PROJ_SPEC['tool']['bl_ext']['packaging']['init_settings_filename'],
				tomli_w.dumps(json.loads(init_settings.model_dump_json())),
			)
		info.console.log('Wrote Init Settings.')

		# Install Addon Files @ /*
		with info.console.status('Writing Addon Files...'):
			for file_to_zip in info.PATH_PKG.rglob('*'):
				f_zip.write(file_to_zip, file_to_zip.relative_to(info.PATH_PKG.parent))
		info.console.log('Wrote Addon Files.')

		# Install Wheels @ /wheels/*
		# with info.console.status('Writing Wheels...'):
		# for wheel_to_zip in info.PATH_WHEELS.rglob('*'):
		# f_zip.write(wheel_to_zip, Path('wheels') / wheel_to_zip.name)
		# info.console.log('Wrote Wheels.')

		total_wheel_size = sum(
			f.stat().st_size for f in info.PATH_WHEELS.rglob('*') if f.is_file()
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
		with rich.progress.Live(progress, console=info.console, transient=True) as live:
			for wheel_to_zip in info.PATH_WHEELS.rglob('*.whl'):
				f_zip.write(wheel_to_zip, Path('wheels') / wheel_to_zip.name)
				progress.update(
					progress_task,
					description=wheel_to_zip.name,
					advance=wheel_to_zip.stat().st_size,
				)
				live.refresh()

		info.console.log('Wrote Wheels.')

	# Delete the ZIP
	info.console.rule(f'[bold green] Extension Packed to {info.PATH_ZIP}!')


####################
# - Run Blender w/Clean Addon Reinstall
####################
if __name__ == '__main__':
	profile = sys.argv[1]
	if sys.argv[1] in ['dev', 'release', 'release-debug']:
		if not list(info.PATH_WHEELS.iterdir()) or '--download-wheels' in sys.argv:
			download_wheels()

		pack_bl_extension(profile)
	else:
		msg = f'Packaging profile "{profile}" is invalid. Refer to source of pack.py for more information'
		raise ValueError(msg)
