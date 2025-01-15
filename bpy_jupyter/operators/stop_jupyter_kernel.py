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

import asyncio
import typing as typ

import bpy

from .. import contracts as ct
from ..services import jupyter_kernel as jkern


class StopJupyterKernel(bpy.types.Operator):
	"""Stop a notebook kernel and Jupyter Lab server running within Blender."""

	bl_idname = ct.OperatorType.StopJupyterKernel
	bl_label = 'Stop Jupyter Kernel'

	@classmethod
	def poll(cls, _: bpy.types.Context) -> bool:
		return jkern.is_kernel_running() and not jkern.is_kernel_waiting_to_stop()

	def execute(self, context: bpy.types.Context) -> set[ct.BLOperatorStatus]:
		jkern.queue_kernel_stop()
		return {'FINISHED'}


####################
# - Blender Registration
####################
BL_REGISTER = [StopJupyterKernel]
BL_HANDLERS: ct.BLHandlers = ct.BLHandlers()
BL_KEYMAP_ITEMS: list[ct.BLKeymapItem] = []
