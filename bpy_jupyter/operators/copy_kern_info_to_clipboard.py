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

"""Implements `CopyJupyURLToClip`.

Attributes:
	BL_REGISTER: All the Blender classes, implemented by this module, that should be registered.
"""

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
class CopyKernelInfoToClipboard(bpy.types.Operator):
	"""Copy a value to the system clipboard.

	Attributes:
		bl_idname: Name of this operator type.
		bl_label: Human-oriented label for this operator.
		value_to_copy: Operator property containing the string to copy.
	"""

	bl_idname: str = OperatorType.CopyKernelInfoToClipboard
	bl_label: str = 'Copy Kernel Connection Path'

	value_to_copy: bpy.props.StringProperty('')  # pyright: ignore[reportInvalidTypeForm, reportCallIssue, reportUninitializedInstanceVariable]

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
		pyperclipfix.copy(str(self.value_to_copy))  # pyright: ignore[reportUnknownArgumentType]

		self.report(
			{'INFO'},
			'Copied Jupyter Kernel Value to Clipboard',
		)
		return {'FINISHED'}


####################
# - Blender Registration
####################
BL_REGISTER = [CopyKernelInfoToClipboard]
