import enum
import os as _os
import shutil
import subprocess

import rich
import typer

from . import pack, paths, spec

console = rich.console.Console()
app = typer.Typer()


class SupportedOS(enum.StrEnum):
	"""Operating systems supported by Blender extensions managed by BLExt."""

	linux_x64 = 'linux-x64'
	mac_arm = 'mac-arm64'
	windows_amd64 = 'windows-amd64'


ALL_SUPPORTED_OSES: tuple[SupportedOS, ...] = (
	SupportedOS.linux_x64,
	SupportedOS.mac_arm,
	SupportedOS.windows_amd64,
)


class SupportedProfile(enum.StrEnum):
	"""Release profiles supported by Blender extensions managed by BLExt."""

	test = 'test'
	dev = 'dev'
	release = 'release'
	release_debug = 'release-debug'


@app.command()
def build(
	os: SupportedOS = SupportedOS.linux_x64,
	profile: SupportedProfile = SupportedProfile.release,
	delete_existing_wheels: bool = True,
) -> None:
	"""Build the Blender extension to an installable `.zip` file."""
	# Load Specification
	blext_spec = spec.load_blext_spec(profile).constrain_to_os(os)

	# Download Wheels
	pack.download_wheels(
		blext_spec,
		os=os,
		delete_existing_wheels=delete_existing_wheels,
	)

	# Pack the Blender Extension
	pack.pack_bl_extension(blext_spec, overwrite=True)
	path_zip = paths.PATH_BUILD / blext_spec.zip_filename()

	# Validate the Blender Extension
	console.rule('[bold yellow] Extension Validation...')
	bl_process = subprocess.Popen(
		[
			'--no-addons',  ## For some reason this must be here lol
			'--factory-startup',  ## Temporarily Disable All Addons
			'--command',  ## Validate an Extension
			'extension',
			'validate',
			str(path_zip),
		],
		bufsize=0,  ## TODO: Check if -1 is OK
		executable=shutil.which('blender'),
		env=_os.environ,
	)
	bl_process.wait()


## TODO: Detect the current OS and use that as the default.
@app.command()
def dev(
	os: SupportedOS = SupportedOS.linux_x64,
	download_wheels: bool = True,
	delete_existing_wheels: bool = False,
) -> None:
	"""Launch Blender with the extension installed."""
	profile = 'dev'

	# Load Specification
	blext_spec = spec.load_blext_spec(profile).constrain_to_os(os)

	# Download Wheels
	if download_wheels:
		pack.download_wheels(
			blext_spec,
			os=os,
			delete_existing_wheels=delete_existing_wheels,
		)

	# Pack the Blender Extension
	pack.pack_bl_extension(blext_spec, overwrite=True)

	# Launch Blender
	## - Same as running 'blender --python ./blender_scripts/bl_init.py'
	path_zip = paths.PATH_BUILD / blext_spec.zip_filename()
	path_bl_init_script = paths.PATH_ROOT / 'blext' / 'blender_python' / 'bl_init.py'

	bl_process = subprocess.Popen(
		[
			'--no-addons',  ## For some reason this must be here lol
			'--python',
			str(path_bl_init_script),
			'--factory-startup',  ## Temporarily Disable All Addons
		],
		bufsize=0,  ## TODO: Check if -1 is OK
		executable=shutil.which('blender'),
		env=_os.environ
		| {
			'BLEXT_ADDON_NAME': blext_spec.id,
			'BLEXT_ZIP_PATH': str(path_zip),
			'BLEXT_LOCAL_PATH': str(paths.PATH_LOCAL),
		},
	)
	bl_process.wait()
