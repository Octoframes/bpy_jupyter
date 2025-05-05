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

"""Manages the registration of Blender classes.

Attributes:
	_REGISTERED_CLASSES: Blender classes currently registered by this addon, indexed by `bl_idname`.
"""

import collections.abc as cabc

import bpy

from .types import BLClass

####################
# - Globals
####################
_REGISTERED_CLASSES = dict[str, type[BLClass]]()


####################
# - Class Registration
####################
def register_classes(bl_classes: cabc.Sequence[type[BLClass]]) -> None:
	"""Registers a list of Blender classes.

	Notes:
		If a class is already registered (aka. its `bl_idname` already has an entry), then its registration is skipped.

	Parameters:
		bl_register: List of Blender classes to register.
	"""
	for cls in bl_classes:
		if cls.bl_idname in _REGISTERED_CLASSES:
			continue

		bpy.utils.register_class(cls)
		_REGISTERED_CLASSES[cls.bl_idname] = cls


def unregister_classes() -> None:
	"""Unregisters all previously registered Blender classes."""
	for cls in reversed(_REGISTERED_CLASSES.values()):
		bpy.utils.unregister_class(cls)

	_REGISTERED_CLASSES.clear()
