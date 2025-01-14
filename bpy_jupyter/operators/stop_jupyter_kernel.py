"""Defines the `StopJupyterKernel` operator.

Inspired by <https://github.com/cheng-chi/blender_notebook/blob/master/blender_notebook/kernel.py>
"""

import asyncio
import typing as typ

import bpy

from .. import contracts as ct
from ..services import jupyter_kernel as jkern


class StopJupyterKernel(bpy.types.Operator):
	"""Operator that starts a Jupyter kernel within Blender."""

	bl_idname = ct.OperatorType.StopJupyterKernel
	bl_label = 'Stop Jupyter Kernel'

	@classmethod
	def poll(cls, _: bpy.types.Context) -> bool:
		return jkern.is_kernel_running() and not jkern.is_kernel_waiting_to_stop()

	def execute(self, context: bpy.types.Context) -> set[ct.BLOperatorStatus]:
		jkern.queue_kernel_stop()
		return {'FINISHED'}


####################
# - Blender Registration
####################
BL_REGISTER = [StopJupyterKernel]
BL_HANDLERS: ct.BLHandlers = ct.BLHandlers()
BL_KEYMAP_ITEMS: list[ct.BLKeymapItem] = []
