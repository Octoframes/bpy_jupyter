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

"""Implements `StartJupyterKernel`.

Attributes:
	BL_REGISTER: All the Blender classes, implemented by this module, that should be registered.
"""

import typing as typ
from pathlib import Path

import bpy
import typing_extensions as typ_ext

from ..services import async_event_loop, jupyter_kernel
from ..types import EXT_PACKAGE, OperatorType

if typ.TYPE_CHECKING:
	from bpy._typing import rna_enums


####################
# - Class: Start Jupyter Kernel
####################
class StartJupyterKernel(bpy.types.Operator):
	"""Start a notebook kernel, and Jupyter Lab server, from within Blender.

	Attributes:
		bl_idname: Name of this operator type.
		bl_label: Human-oriented label for this operator.
	"""

	bl_idname: str = OperatorType.StartJupyterKernel
	bl_label: str = 'Start Jupyter Kernel'

	@typ_ext.override
	@classmethod
	def poll(cls, context: bpy.types.Context) -> bool:
		"""Can run while a Jupyter kernel is not running.

		Parameters:
			context: The current `bpy` context.
				_Not used._
		"""
		return not jupyter_kernel.is_kernel_running()

	@typ_ext.override
	def execute(
		self, context: bpy.types.Context
	) -> set['rna_enums.OperatorReturnItems']:
		"""Start an embedded jupyter kernel, as well as an `asyncio` event loop to handle kernel clients.

		Parameters:
			context: The current `bpy` context.
				_Not used._
		"""
		path_extension_user = Path(
			bpy.utils.extension_path_user(
				EXT_PACKAGE,
				path='',
				create=True,
			)
		).resolve()

		# (Re)Initialize Jupyter Kernel
		jupyter_kernel.init(
			path_connection_file=Path(
				path_extension_user / '.jupyter-connections' / 'connection.json'
			),
		)

		# Start Jupyter Kernel and asyncio Event Loop
		if jupyter_kernel.IPYKERNEL is not None:
			jupyter_kernel.IPYKERNEL.start()
			async_event_loop.start()

		return {'FINISHED'}


####################
# - Blender Registration
####################
BL_REGISTER = [StartJupyterKernel]
