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

import ipaddress
from pathlib import Path

import bpy

from .. import __package__ as extension_package
from ..services import async_event_loop, jupyter_kernel
from ..types import BLOperatorStatus, OperatorType


class StartJupyterKernel(bpy.types.Operator):
	"""Start a notebook kernel, and Jupyter Lab server, from within Blender."""

	bl_idname = OperatorType.StartJupyterKernel
	bl_label = 'Start Jupyter Kernel'

	@classmethod
	def poll(cls, _: bpy.types.Context) -> bool:
		"""Allow running this operator when no kernel is running."""
		return not jupyter_kernel.is_kernel_running()

	def execute(self, context: bpy.types.Context) -> BLOperatorStatus:
		"""Initialize and run an `IPyKernel` and (optionally) `JupyterLabServer`."""
		path_extension_user = Path(
			bpy.utils.extension_path_user(
				extension_package,
				path='',
				create=True,
			)
		).resolve()

		# Initialize Jupyter Kernel + Server
		print('starting the start')
		jupyter_kernel.init(
			path_connection_file=Path(
				path_extension_user / '.jupyter-connections' / 'connection.json'
			),
		)

		# Start Jupyter Kernel
		print('starting')
		if jupyter_kernel.IPYKERNEL is not None:
			jupyter_kernel.IPYKERNEL.start()
		print('can you see me?')

		# Start Event Loop
		async_event_loop.start()

		return {'FINISHED'}


####################
# - Blender Registration
####################
BL_REGISTER = [StartJupyterKernel]
