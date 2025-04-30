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
		scene = context.scene
		path_extension_user = Path(
			bpy.utils.extension_path_user(
				extension_package,
				path='',
				create=True,
			)
		).resolve()

		# Initialize Jupyter Kernel + Server
		jupyter_kernel.init(
			path_connection_file=Path(
				path_extension_user / '.jupyter-connections' / 'connection.json'
			),
			path_notebooks=Path(bpy.path.abspath(scene.jupyter_notebook_dir)),
			jupyter_ip=ipaddress.IPv4Address(scene.jupyter_ip),
			jupyter_port=scene.jupyter_port,
		)

		# Start Jupyter Kernel
		if jupyter_kernel.IPYKERNEL is not None:
			jupyter_kernel.IPYKERNEL.start()

		# Start Jupyter Server
		##if jupyter_kernel.JUPYTER_LAB_SERVER is not None:
		##	jupyter_kernel.JUPYTER_LAB_SERVER.start(
		##		launch_browser=scene.jupyter_launch_browser
		##	)

		# Start Event Loop
		async_event_loop.start()

		return {'FINISHED'}


####################
# - Blender Registration
####################
BL_REGISTER = [StartJupyterKernel]
