"""Blender operators that ship with `bpy_jupyter`."""

from functools import reduce

from .. import contracts as ct
from . import start_jupyter_kernel, stop_jupyter_kernel

BL_REGISTER: list[ct.BLClass] = [
	*start_jupyter_kernel.BL_REGISTER,
	*stop_jupyter_kernel.BL_REGISTER,
]
BL_HANDLERS: ct.BLHandlers = reduce(
	lambda a, b: a + b,
	[
		start_jupyter_kernel.BL_HANDLERS,
		stop_jupyter_kernel.BL_HANDLERS,
	],
	ct.BLHandlers(),
)
BL_KEYMAP_ITEMS: list[ct.BLKeymapItem] = [
	*start_jupyter_kernel.BL_KEYMAP_ITEMS,
	*stop_jupyter_kernel.BL_KEYMAP_ITEMS,
]
