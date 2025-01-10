"""Declares types for working with `bpy.types.KeyMap`s."""

import bpy
import pydantic as pyd

from .bl import BLEventType, BLEventValue, BLSpaceType
from .operator_types import OperatorType


class BLKeymapItem(pyd.BaseModel):
	"""Contains lists of handlers associated with this addon."""

	operator: OperatorType

	event_type: BLEventType
	event_value: BLEventValue

	shift: bool = False
	ctrl: bool = False
	alt: bool = False
	key_modifier: BLEventType = 'NONE'

	space_type: BLSpaceType = 'EMPTY'

	def register(self, addon_keymap: bpy.types.KeyMap) -> bpy.types.KeyMapItem:
		"""Registers this hotkey with an addon keymap.

		Raises:
			ValueError: If the `space_type` constraint of the addon keymap does not match the `space_type` constraint of this `BLKeymapItem`.
		"""
		if self.space_type == addon_keymap.space_type:
			addon_keymap.keymap_items.new(
				self.operator,
				self.event_type,
				self.event_value,
				shift=self.shift,
				ctrl=self.ctrl,
				alt=self.alt,
				key_modifier=self.key_modifier,
			)

		msg = f'Addon keymap space type {addon_keymap.space_type} does not match space_type of BLKeymapItem to register: {self}'
		raise ValueError(msg)
		## TODO: Check if space_type matches?
