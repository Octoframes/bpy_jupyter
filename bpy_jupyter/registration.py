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

"""Manages the registration of Blender classes, including delayed registrations that require access to Python dependencies.

Attributes:
	_REGISTERED_CLASSES: Blender classes currently registered by this addon.
	_REGISTERED_KEYMAPS: Addon keymaps currently registered by this addon.
		Each addon keymap is constrained to a single `space_type`, which is the key.
	_REGISTERED_KEYMAP_ITEMS: Addon keymap items currently registered by this addon.
		Each keymap item is paired to the keymap within which it is registered.
		_Each keymap is guaranteed to also be found in `_REGISTERED_KEYMAPS`._
	_REGISTERED_HANDLERS: Addon handlers currently registered by this addon.
"""

import typing as typ

import bpy

from .types import BLClass

####################
# - Globals
####################
_REGISTERED_CLASSES = list[BLClass]()


####################
# - Class Registration
####################
def register_classes(bl_classes: list[BLClass]) -> None:
	"""Registers a list of Blender classes.

	Parameters:
		bl_register: List of Blender classes to register.
	"""
	for cls in bl_classes:
		if cls.bl_idname in _REGISTERED_CLASSES:
			continue

		bpy.utils.register_class(cls)
		_REGISTERED_CLASSES.append(cls)


def unregister_classes() -> None:
	"""Unregisters all previously registered Blender classes."""
	for cls in reversed(_REGISTERED_CLASSES):
		bpy.utils.unregister_class(cls)

	_REGISTERED_CLASSES.clear()
