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

import bpy

from ..types import OperatorType, PanelType


####################
# - Scene Properties
####################
class JupyterPanel(bpy.types.Panel):
	"""'Controls the Jupyter kernel launched using Blender."""

	## TODO: Provide an option that forces appending? So that users can modify from a baseline. Just watch out - dealing with overlaps isn't trivial.

	bl_idname = PanelType.JupyterPanel
	bl_label = 'Jupyter Kernels'
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = 'scene'

	def draw(self, _: bpy.types.Context) -> None:
		"""Draw the Jupyter panel w/options.

		Notes:
			Run by Blender when the panel needs to be displayed.

		Parameters:
			context: The Blender context object.
				Must contain `context.window_manager` and `context.workspace`.
		"""
		layout = self.layout

		####################
		# - Section: Stop/Start Kernel
		####################
		# Operator: Start Kernel
		row = layout.row(align=True)
		row.operator(OperatorType.StartJupyterKernel)

		# Operator: Stop Kernel
		row = layout.row(align=True)
		row.operator(OperatorType.StopJupyterKernel)

		####################
		# - Section: Copyable URLs
		####################
		header, body = layout.panel(
			'jupyter_copy_urls_subpanel',
			default_closed=False,
		)
		header.label(text='Copy to Clipboard')
		if body is not None:
			# Operators
			row = body.row(align=False)
			op = row.operator(OperatorType.CopyKernConnPath)


####################
# - Blender Registration
####################
BL_REGISTER = [JupyterPanel]
