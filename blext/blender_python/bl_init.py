import os
import sys
from pathlib import Path

import bpy

####################
# - Constants
####################
# Addon Name
if os.environ.get('BLEXT_ADDON_NAME') is not None:
	BLEXT_ADDON_NAME = os.environ['BLEXT_ADDON_NAME']
else:
	msg = "The env var 'BLEXT_ADDON_NAME' must be available, but it is not"
	raise ValueError(msg)

# Zip Path
if os.environ.get('BLEXT_ZIP_PATH') is not None:
	BLEXT_ZIP_PATH = Path(os.environ['BLEXT_ZIP_PATH'])
else:
	msg = "The env var 'BLEXT_ZIP_PATH' must be available, but it is not"
	raise ValueError(msg)

# Local Path
if os.environ.get('BLEXT_ZIP_PATH') is not None:
	BLEXT_LOCAL_PATH = Path(os.environ['BLEXT_LOCAL_PATH'])
else:
	msg = "The env var 'BLEXT_LOCAL_PATH' must be available, but it is not"
	raise ValueError(msg)

BLEXT_DEV_REPO_NAME = 'blext_dev_repo'


####################
# - main()
####################
if __name__ == '__main__':
	# Suppress Splash Screen
	## - It just gets in the way.
	bpy.context.preferences.view.show_splash = False

	# Check for Local Dev Repo
	## - Create if non-existant.
	if BLEXT_DEV_REPO_NAME not in {
		repo.name for repo in bpy.context.preferences.extensions.repos
	}:
		bpy.ops.preferences.extension_repo_add(
			name=BLEXT_DEV_REPO_NAME,
			remote_url='',
			use_access_token=False,
			use_sync_on_startup=False,
			# use_custom_directory=True,
			# custom_directory=str(BLEXT_LOCAL_PATH),
			type='LOCAL',
		)

	# Get the Repository Index of Local Dev Repo
	dev_repo_idx = next(
		repo_idx
		for repo_idx, repo in enumerate(bpy.context.preferences.extensions.repos)
		if repo.name == BLEXT_DEV_REPO_NAME
	)
	dev_repo_module = next(
		repo.module
		for repo_idx, repo in enumerate(bpy.context.preferences.extensions.repos)
		if repo.name == BLEXT_DEV_REPO_NAME
	)

	# Uninstall Existing Addon
	if BLEXT_ADDON_NAME in bpy.context.preferences.addons.keys():  # noqa: SIM118
		bpy.ops.extensions.package_uninstall(
			repo_index=dev_repo_idx,
			pkg_id=BLEXT_ADDON_NAME,
		)

		# Vacuum sys.modules (remove bl_ext.<addon_repo>.<addon_name>)
		## - TODO: Start conversation upstream abt. overlapping dependencies.
		if f'blext.{BLEXT_DEV_REPO_NAME}.{BLEXT_ADDON_NAME}' in sys.modules:
			del sys.modules[BLEXT_ADDON_NAME]

	# Install New Extension
	bpy.ops.extensions.package_install_files(
		'INVOKE_DEFAULT',
		repo=dev_repo_module,
		filepath=str(BLEXT_ZIP_PATH),
		enable_on_install=True,
	)
