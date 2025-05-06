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

"""Addon preferences, encapsulating the various global modifications that the user may make to how this addon functions.

Attributes:
	BL_REGISTER: All Blender classes from this module that should be registered.
"""

import bpy

from .types import EXT_PACKAGE


####################
# - Class: Preferences
####################
class BPYJupyterAddonPrefs(bpy.types.AddonPreferences):
	"""Manages user preferences and settings for this addon.

	Attributes:
		bl_idname: Matches `__package__`.
	"""

	bl_idname: str = EXT_PACKAGE


####################
# - Blender Registration
####################
BL_REGISTER = [BPYJupyterAddonPrefs]
