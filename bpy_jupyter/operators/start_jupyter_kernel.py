"""Defines the `StartJupyterKernel` operator.

Inspired by <https://github.com/cheng-chi/blender_notebook/blob/master/blender_notebook/kernel.py>
"""

import asyncio
import ipaddress
from pathlib import Path

import bpy

from .. import contracts as ct
from ..services import jupyter_kernel as jkern


class StartJupyterKernel(bpy.types.Operator):
	"""Operator that starts a Jupyter kernel within Blender."""

	bl_idname = ct.OperatorType.StartJupyterKernel
	bl_label = 'Start Jupyter Kernel'

	_timer = None

	def modal(
		self, context: bpy.types.Context, event: bpy.types.Event
	) -> set[ct.BLOperatorStatus]:
		if jkern.is_kernel_waiting_to_stop():
			# Stop the Timer
			wm = context.window_manager
			wm.event_timer_remove(self._timer)

			self._timer = None

			# Stop the Kernel
			jkern.stop_kernel()

			# Conclude the Modal Operator
			return {'FINISHED'}

		if event.type == 'TIMER' and not jkern.is_kernel_waiting_to_stop():
			# Flush Pending ASync Commands
			loop = asyncio.get_event_loop()
			loop.call_soon(loop.stop)
			loop.run_forever()

		return {'PASS_THROUGH'}

	@classmethod
	def poll(cls, context: bpy.types.Context) -> bool:
		return not jkern.is_kernel_running()

	def execute(self, context: bpy.types.Context) -> set[ct.BLOperatorStatus]:
		# Setup Timer
		wm = context.window_manager
		self._timer = wm.event_timer_add(0.016, window=context.window)
		wm.modal_handler_add(self)

		# Retrieve Scene Properties from Context
		kernel_type = context.scene.jupyter_kernel_type
		notebook_dir = context.scene.jupyter_notebook_dir
		launch_browser = context.scene.jupyter_launch_browser
		jupyter_ip = context.scene.jupyter_ip
		jupyter_port = context.scene.jupyter_port

		match kernel_type:
			case 'IPYKERNEL':
				jkern.start_kernel(
					addon_dir=ct.addon.addon_dir(),
					kernel_type=kernel_type,
					notebook_dir=Path(bpy.path.abspath(notebook_dir)),
					launch_browser=launch_browser,
					jupyter_ip=ipaddress.IPv4Address(jupyter_ip),
					jupyter_port=jupyter_port,
				)

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
