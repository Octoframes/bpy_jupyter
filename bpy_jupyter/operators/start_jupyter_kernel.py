"""Defines the `StartJupyterKernel` operator.

Inspired by <https://github.com/cheng-chi/blender_notebook/blob/master/blender_notebook/kernel.py>
"""

import asyncio

import bpy

from .. import contracts as ct
from ..services import jupyter_kernel as jkern


class StartJupyterKernel(bpy.types.Operator):
	"""Operator that starts a Jupyter kernel within Blender."""

	bl_idname = ct.OperatorType.StartJupyterKernel
	bl_label = 'Start Jupyter Kernel'

	kernel_type: bpy.props.EnumProperty(
		name='Kernel Type',
		description='The jupyter kernel to launch within Blender',
		items=[
			(
				'IPYKERNEL',
				'IPyKernel',
				'A traditional, well-tested Python notebook kernel',
			),
			(
				'MARIMO',
				'Marimo',
				'A reactive, modern Python notebook kernel',
			),
		],
		default='IPYKERNEL',
	)

	_timer = None

	def modal(
		self, context: bpy.types.Context, event: bpy.types.Event
	) -> set[ct.BLOperatorStatus]:
		if event.type == 'TIMER':
			loop = asyncio.get_event_loop()
			loop.call_soon(loop.stop)
			loop.run_forever()

		if jkern.kernel_should_stop():
			jkern.stop_kernel()

			wm = context.window_manager
			wm.event_timer_remove(self._timer)

			self._timer = None

			return {'FINISHED'}

		return {'PASS_THROUGH'}

	@classmethod
	def poll(cls, context: bpy.types.Context) -> bool:
		return not jkern.is_kernel_running()

	def execute(self, context: bpy.types.Context) -> set[ct.BLOperatorStatus]:
		wm = context.window_manager
		self._timer = wm.event_timer_add(0.016, window=context.window)
		wm.modal_handler_add(self)

		match self.kernel_type:
			case 'IPYKERNEL':
				jkern.start_kernel(ct.addon.addon_dir())

			case 'MARIMO':
				msg = 'Marimo kernel is not yet implemented.'
				raise NotImplementedError(msg)

		return {'RUNNING_MODAL'}

	def cancel(self, context):
		jkern.stop_kernel()

		wm = context.window_manager
		wm.event_timer_remove(self._timer)

		self._timer = None


####################
# - Blender Registration
####################
BL_REGISTER = [StartJupyterKernel]
BL_HANDLERS: ct.BLHandlers = ct.BLHandlers()
BL_KEYMAP_ITEMS: list[ct.BLKeymapItem] = []
