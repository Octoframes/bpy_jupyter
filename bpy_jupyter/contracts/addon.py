"""Addon information deduced from the manifest and `bpy`."""

import tomllib
from pathlib import Path

import bpy

from .. import __package__ as base_package

PATH_ADDON_ROOT: Path = Path(__file__).resolve().parent.parent
PATH_MANIFEST: Path = PATH_ADDON_ROOT / 'blender_manifest.toml'

with PATH_MANIFEST.open('rb') as f:
	MANIFEST = tomllib.load(f)

NAME: str = MANIFEST['id']
VERSION: str = MANIFEST['version']


####################
# - Dynamic Access
####################
def prefs() -> bpy.types.AddonPreferences | None:
	"""Retrieve the preferences of this addon, if they are available yet.

	Notes:
		While registering the addon, one may wish to use the addon preferences.
		This isn't possible - not even for default values.

		Either a bad idea is at work, or `oscillode.utils.init_settings` should be consulted until the preferences are available.

	Returns:
		The addon preferences, if the addon is registered and loaded - otherwise None.
	"""
	addon = bpy.context.preferences.addons.get(base_package)
	if addon is None:
		return None
	return addon.preferences


def addon_dir() -> Path:
	"""Absolute path to a local addon-specific directory guaranteed to be writable."""
	return Path(
		bpy.utils.extension_path_user(
			base_package,
			path='',
			create=True,
		)
	).resolve()
