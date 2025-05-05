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

"""Implements `JupyterPanel`."""

import typing as typ

import bpy
import typing_extensions as typ_ext

if typ.TYPE_CHECKING:
	from bpy._typing import rna_enums


from ..types import BLContextType, OperatorType, PanelType


####################
# - Scene Properties
####################
class JupyterPanel(bpy.types.Panel):
	"""Control the Jupyter kernel launched using Blender.

	Attributes:
		bl_idname: Name of this panel type.
		bl_label: Human-oriented label for this panel.
		bl_space_type: The space to display this panel in.
		bl_region_type: The region to display this panel in.
		bl_context: Extra context guiding where this panel should be placed.
	"""

	bl_idname: str = PanelType.JupyterPanel
	bl_label: str = 'Jupyter Kernels'
	bl_space_type: 'rna_enums.SpaceTypeItems' = 'PROPERTIES'
	bl_region_type: 'rna_enums.RegionTypeItems' = 'WINDOW'
	bl_context: BLContextType = 'scene'  # pyright: ignore[reportIncompatibleVariableOverride]

	@typ_ext.override
	def draw(self, context: bpy.types.Context) -> None:
		"""Draw the Jupyter kernel panel, including a few options.

		Notes:
			Run by Blender when the panel needs to be displayed.

		Parameters:
			context: The Blender context object.
				Must contain `context.window_manager` and `context.workspace`.
		"""
		layout = self.layout
		if layout is None:
			return

		####################
		# - Section: Stop/Start Kernel
		####################
		# Operator: Start Kernel
		row = layout.row(align=True)
		_ = row.operator(OperatorType.StartJupyterKernel)

		# Operator: Stop Kernel
		row = layout.row(align=True)
		_ = row.operator(OperatorType.StopJupyterKernel)

		####################
		# - Section: Copyable URLs
		####################
		header, body = layout.panel(
			PanelType.JupyterPanel + '_copy_urls_subpanel',
			default_closed=False,
		)
		header.label(text='Copy to Clipboard')
		if body is not None:  # pyright: ignore[reportUnnecessaryComparison]
			# Operators
			row = body.row(align=False)
			_ = row.operator(OperatorType.CopyKernConnPath)


####################
# - Blender Registration
####################
BL_REGISTER = [JupyterPanel]
