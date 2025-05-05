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

"""Defines the `CopyJupyURLToClip` operator."""

import typing as typ

import bpy
import pyperclipfix
import typing_extensions as typ_ext

from ..services import jupyter_kernel
from ..types import OperatorType

if typ.TYPE_CHECKING:
	from bpy._typing import rna_enums


####################
# - Constants
####################
class CopyKernConnPath(bpy.types.Operator):
	"""Copy the path to the kernel connection file to the clipboard.

	Attributes:
		bl_idname: Name of this operator type.
		bl_label: Human-oriented label for this operator.
	"""

	bl_idname: str = OperatorType.CopyKernConnPath
	bl_label: str = 'Copy Kernel Connection Path'

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
		"""Copy the path to the running connection file, to the system clipboard.

		Parameters:
			context: The current `bpy` context.
				_Not used._
		"""
		if jupyter_kernel.IPYKERNEL is None:
			msg = "IPyKernel is `None`. This is a bug - generally, `poll()` should guarantee that this doesn't happen."
			raise RuntimeError(msg)

		path_connection_file = jupyter_kernel.IPYKERNEL.path_connection_file
		pyperclipfix.copy(str(path_connection_file))

		self.report(
			{'INFO'},
			'Copied IPyKernel Connection File Path to Clipboard.',
		)
		return {'FINISHED'}


####################
# - Blender Registration
####################
BL_REGISTER = [CopyKernConnPath]
