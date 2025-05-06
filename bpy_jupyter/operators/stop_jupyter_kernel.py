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

"""Implements `StopJupyterKernel`.

Attributes:
	BL_REGISTER: All the Blender classes, implemented by this module, that should be registered.
"""

import typing as typ

import bpy
import typing_extensions as typ_ext

from ..services import async_event_loop, jupyter_kernel
from ..types import OperatorType

if typ.TYPE_CHECKING:
	from bpy._typing import rna_enums


####################
# - Class: Stop Jupyter Kernel
####################
class StopJupyterKernel(bpy.types.Operator):
	"""Stop a notebook kernel and Jupyter Lab server running within Blender.

	Attributes:
		bl_idname: Name of this operator type.
		bl_label: Human-oriented label for this operator.
	"""

	bl_idname: str = OperatorType.StopJupyterKernel
	bl_label: str = 'Stop Jupyter Kernel'

	@typ_ext.override
	@classmethod
	def poll(cls, context: bpy.types.Context) -> bool:
		"""Can run while a Jupyter kernel is running.

		Parameters:
			context: The current `bpy` context.
				_Not used._
		"""
		return jupyter_kernel.is_kernel_running()

	@typ_ext.override
	def execute(
		self, context: bpy.types.Context
	) -> set['rna_enums.OperatorReturnItems']:
		"""Start the embedded jupyter kernel, as well as the `asyncio` event loop managed by this extension.

		Parameters:
			context: The current `bpy` context.
				_Not used._
		"""
		# Stop Jupyter Kernel and asyncio Event Loop
		if jupyter_kernel.IPYKERNEL is not None:
			jupyter_kernel.IPYKERNEL.stop()
			async_event_loop.stop()

		return {'FINISHED'}


####################
# - Blender Registration
####################
BL_REGISTER = [StopJupyterKernel]
