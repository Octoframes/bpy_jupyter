# bpy_jupyter
# Copyright (C) 2025 bpy_jupyter Project Contributors
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
