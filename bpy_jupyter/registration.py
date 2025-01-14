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

import bpy

from . import contracts as ct
from .utils import logger

log = logger.get(__name__)

####################
# - Globals
####################
_REGISTERED_CLASSES: list[ct.BLClass] = []

_REGISTERED_KEYMAPS: dict[ct.BLSpaceType, bpy.types.KeyMap] = {}
_REGISTERED_KEYMAP_ITEMS: list[tuple[bpy.types.KeyMap, bpy.types.KeyMapItem]] = []

_REGISTERED_HANDLERS: ct.BLHandlers | None = None


####################
# - Class Registration
####################
def register_classes(bl_register: list[ct.BLClass]) -> None:
	"""Registers a list of Blender classes.

	Parameters:
		bl_register: List of Blender classes to register.
	"""
	log.info('Registering %s Classes', len(bl_register))
	for cls in bl_register:
		if cls.bl_idname in _REGISTERED_CLASSES:
			msg = f'Skipping register of {cls.bl_idname}'
			log.info(msg)
			continue

		log.debug(
			'Registering Class %s',
			repr(cls),
		)
		bpy.utils.register_class(cls)
		_REGISTERED_CLASSES.append(cls)


def unregister_classes() -> None:
	"""Unregisters all previously registered Blender classes."""
	log.info('Unregistering %s Classes', len(_REGISTERED_CLASSES))
	for cls in reversed(_REGISTERED_CLASSES):
		log.debug(
			'Unregistering Class %s',
			repr(cls),
		)
		bpy.utils.unregister_class(cls)

	_REGISTERED_CLASSES.clear()


####################
# - Handler Registration
####################
def register_handlers(bl_handlers: ct.BLHandlers) -> None:
	"""Register the given Blender handlers."""
	global _REGISTERED_HANDLERS  # noqa: PLW0603

	log.info('Registering BLHandlers')  ## TODO: More information
	if _REGISTERED_HANDLERS is None:
		bl_handlers.register()
		_REGISTERED_HANDLERS = bl_handlers
	else:
		msg = 'There are already BLHandlers registered; they must be unregistered before a new set can be registered.'
		raise ValueError(msg)


def unregister_handlers() -> None:
	"""Unregister this addon's registered Blender handlers."""
	global _REGISTERED_HANDLERS  # noqa: PLW0603

	log.info('Unregistering BLHandlers')  ## TODO: More information
	if _REGISTERED_HANDLERS is not None:
		_REGISTERED_HANDLERS.register()
		_REGISTERED_HANDLERS = None
	else:
		msg = 'There are no BLHandlers registered; therefore, there is nothing to register.'
		raise ValueError(msg)


####################
# - Keymap Registration
####################
def register_keymaps(keymap_items: list[ct.BLKeymapItem]) -> None:
	"""Registers a list of Blender hotkey definitions.

	Parameters:
		bl_keymap_items: List of Blender hotkey definitions to register.
	"""
	# Aggregate Requested Spaces of All Keymap Items
	keymap_space_types: set[ct.BLSpaceType] = {
		keymap_item.space_type for keymap_item in keymap_items
	}

	# Create Addon Keymap per Requested Space
	for keymap_space_type in keymap_space_types:
		log.info('Registering %s Keymap', keymap_space_type)
		bl_keymap = bpy.context.window_manager.keyconfigs.addon.keymaps.new(
			name=f'{ct.addon.NAME} - {keymap_space_type}',
			space_type=keymap_space_type,
		)
		_REGISTERED_KEYMAPS[keymap_space_type] = bl_keymap

	# Register Keymap Items in Correct Addon Keymap
	for keymap_item in keymap_items:
		log.info('Registering %s Keymap Item', keymap_item)
		bl_keymap = _REGISTERED_KEYMAPS[keymap_item.space_type]
		bl_keymap_item = keymap_item.register(bl_keymap)

		_REGISTERED_KEYMAP_ITEMS.append((bl_keymap, bl_keymap_item))


def unregister_keymaps() -> None:
	"""Unregisters all Blender keymaps associated with the addon."""
	# Unregister Keymap Items from Correct Addon Keymap
	for bl_keymap, bl_keymap_item in reversed(_REGISTERED_KEYMAP_ITEMS):
		log.info('Unregistering %s BL Keymap Item', bl_keymap_item)
		bl_keymap.keymap_items.remove(bl_keymap_item)

	_REGISTERED_KEYMAP_ITEMS.clear()

	# Delete Addon Keymaps
	for bl_keymap in reversed(_REGISTERED_KEYMAPS.values()):
		log.info('Unregistering %s Keymap', bl_keymap)
		bpy.context.window_manager.keyconfigs.addon.keymaps.remove(bl_keymap)

	_REGISTERED_KEYMAPS.clear()
