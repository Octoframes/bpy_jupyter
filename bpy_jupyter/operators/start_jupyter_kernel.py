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
	"""Start a notebook kernel, and Jupyter Lab server, from within Blender."""

	bl_idname = ct.OperatorType.StartJupyterKernel
	bl_label = 'Start Jupyter Kernel'

	_timer = None

	def modal(
		self, context: bpy.types.Context, event: bpy.types.Event
	) -> ct.BLOperatorStatus:
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

	def execute(self, context: bpy.types.Context) -> ct.BLOperatorStatus:
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
