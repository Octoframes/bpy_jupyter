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

"""Defines the `StopJupyterKernel` operator.

Inspired by <https://github.com/cheng-chi/blender_notebook/blob/master/blender_notebook/kernel.py>
"""

import bpy

from ..services import async_event_loop, jupyter_kernel
from ..types import BLOperatorStatus, OperatorType


class StopJupyterKernel(bpy.types.Operator):
	"""Stop a notebook kernel and Jupyter Lab server running within Blender."""

	bl_idname = OperatorType.StopJupyterKernel
	bl_label = 'Stop Jupyter Kernel'

	@classmethod
	def poll(cls, _: bpy.types.Context) -> bool:
		return jupyter_kernel.is_kernel_running()

	def execute(self, _: bpy.types.Context) -> BLOperatorStatus:
		"""Stop a running `IPyKernel` and (optionally) `JupyterLabServer`."""
		print('stopping the stop')

		# Stop Jupyter Kernel
		if jupyter_kernel.IPYKERNEL is not None:
			jupyter_kernel.IPYKERNEL.stop()

		# Stop Event Loop
		async_event_loop.stop()

		print('stopped the stop')

		return {'FINISHED'}


####################
# - Blender Registration
####################
BL_REGISTER = [StopJupyterKernel]
