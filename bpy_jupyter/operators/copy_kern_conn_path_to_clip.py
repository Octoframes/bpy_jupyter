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

"""Defines the `CopyJupyURLToClip` operator.

Inspired by <https://github.com/cheng-chi/blender_notebook/blob/master/blender_notebook/kernel.py>
"""

import bpy
import pyperclipfix

from ..services import jupyter_kernel
from ..types import BLOperatorStatus, OperatorType


####################
# - Constants
####################
class CopyKernConnPath(bpy.types.Operator):
	"""Copy a Jupyter Server URL to the system clipboard. The system clipboard will be cleared after a timeout, unless otherwise altered."""

	bl_idname = OperatorType.CopyKernConnPath
	bl_label = 'Copy Kernel Connection Path'

	@classmethod
	def poll(cls, _: bpy.types.Context) -> bool:
		return jupyter_kernel.is_kernel_running()

	def execute(self, _: bpy.types.Context) -> BLOperatorStatus:
		if jupyter_kernel.IPYKERNEL is not None:
			path_connection_file = jupyter_kernel.IPYKERNEL.path_connection_file
			pyperclipfix.copy(str(path_connection_file))

			self.report(
				{'INFO'},
				'Copied IPyKernel Connection Path to System Clipboard.',
			)
			return {'RUNNING_MODAL'}
		self.report(
			{'ERROR'},
			"IPyKernel hasn't been initialized, and therefore has no connection file path.",
		)
		return {'CANCELLED'}


####################
# - Blender Registration
####################
BL_REGISTER = [CopyKernConnPath]
