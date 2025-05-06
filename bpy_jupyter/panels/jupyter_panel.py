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

"""Implements `JupyterPanel`.

Attributes:
	BL_REGISTER: All the Blender classes, implemented by this module, that should be registered.
"""

import textwrap
import typing as typ

import bpy
import pydantic as pyd
import typing_extensions as typ_ext

from ..services import jupyter_kernel

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
	bl_label: str = 'Jupyter Kernel'
	bl_space_type: 'rna_enums.SpaceTypeItems' = 'PROPERTIES'
	bl_region_type: 'rna_enums.RegionTypeItems' = 'WINDOW'
	bl_context: BLContextType = 'scene'  # pyright: ignore[reportIncompatibleVariableOverride]

	@typ_ext.override
	def draw(self, context: bpy.types.Context) -> None:  # noqa: C901, PLR0912, PLR0915
		"""Draw the Jupyter kernel panel, including a few options.

		Notes:
			Run by Blender when the panel needs to be displayed.

		Parameters:
			context: The Blender context object.
		"""
		if context.region is None or context.preferences is None:
			return

		width_units_nrm = context.region.width / context.preferences.system.dpi
		width_chars = max(int(width_units_nrm / 0.11), 1)

		layout = self.layout
		if layout is None:
			return

		####################
		# - Section: Respect Online Access
		####################
		if not bpy.app.online_access:
			box = layout.box()
			col = box.column()

			row = col.row(align=True)
			row.alignment = 'CENTER'
			row.label(text='Online Access Disabled')

			col.label(text='Required for exposing kernel sockets.')
			col.label(text='1. Open System Preferences.')
			col.label(text='2. Toggle "Allow Online Access".')

			op = box.operator('screen.userpref_show', text='Open System Preferences')
			op.section = 'SYSTEM'  # pyright: ignore[reportAttributeAccessIssue]

		####################
		# - Section: Stop/Start Kernel
		####################
		row = layout.row(align=True)

		col = row.column(align=True)
		col.enabled = bpy.app.online_access
		_ = col.operator(OperatorType.StartJupyterKernel, text='Start Kernel')
		_ = col.operator(OperatorType.StopJupyterKernel, text='Stop Kernel')

		col = row.column(align=True)
		col.scale_y = 2.0
		col.progress(
			text='Active' if jupyter_kernel.is_kernel_running() else 'Inactive',
			factor=1.0 if jupyter_kernel.is_kernel_running() else 0.0,
		)

		####################
		# - Section: Kernel Connection
		####################
		header, body = layout.panel(
			PanelType.JupyterPanel + '_connectionfile',
			default_closed=False,
		)
		header.label(text='Kernel Connection File')
		if body is not None:  # pyright: ignore[reportUnnecessaryComparison]
			####################
			# - Copy File Path | Parent Path | JSON Contents
			####################
			col = body.column(align=True)

			# Copy P
			row = col.row(align=True)
			op = row.operator(
				OperatorType.CopyKernelInfoToClipboard,
				icon='COPYDOWN',
				text='File Path',
			)
			op.value_to_copy = (  # pyright: ignore[reportAttributeAccessIssue]
				str(jupyter_kernel.IPYKERNEL.path_connection_file)
				if jupyter_kernel.IPYKERNEL is not None
				and jupyter_kernel.IPYKERNEL.is_running
				else ''
			)

			op = row.operator(
				OperatorType.CopyKernelInfoToClipboard,
				icon='COPYDOWN',
				text='Parent Path',
			)
			op.value_to_copy = (  # pyright: ignore[reportAttributeAccessIssue]
				str(jupyter_kernel.IPYKERNEL.path_connection_file.parent)
				if jupyter_kernel.IPYKERNEL is not None
				and jupyter_kernel.IPYKERNEL.is_running
				else ''
			)

			op = col.operator(
				OperatorType.CopyKernelInfoToClipboard,
				icon='COPYDOWN',
				text='File JSON Contents',
			)
			op.value_to_copy = (  # pyright: ignore[reportAttributeAccessIssue]
				jupyter_kernel.IPYKERNEL.connection_info.json_str_with_key
				if jupyter_kernel.IPYKERNEL is not None
				and jupyter_kernel.IPYKERNEL.is_running
				else ''
			)

			####################
			# - Label w/File Path
			####################
			subheader, subbody = body.panel(
				PanelType.JupyterPanel + '_connectionfile_path',
				default_closed=True,
			)
			subheader.label(text='File Path')
			if subbody is not None:  # pyright: ignore[reportUnnecessaryComparison]
				if (
					jupyter_kernel.IPYKERNEL is not None
					and jupyter_kernel.IPYKERNEL.is_running
				):
					wrapped_path_connection_file_lines = textwrap.wrap(
						str(jupyter_kernel.IPYKERNEL.path_connection_file),
						width=width_chars,
					)

					box = subbody.box()
					col = box.column(align=False)
					col.scale_y = 0.5

					for line in wrapped_path_connection_file_lines:
						row = col.row(align=True)
						row.alignment = 'CENTER'
						row.label(text=line)
				else:
					box = subbody.box()
					row = box.row(align=False)
					row.alignment = 'CENTER'
					row.label(text='Kernel Inactive')

			####################
			# - Label w/JSON Contents
			####################
			subheader, subbody = body.panel(
				PanelType.JupyterPanel + '_connectionfile_json',
				default_closed=True,
			)
			subheader.label(text='JSON Contents')
			if subbody is not None:  # pyright: ignore[reportUnnecessaryComparison]
				if (
					jupyter_kernel.IPYKERNEL is not None
					and jupyter_kernel.IPYKERNEL.is_running
				):
					wrapped_path_connection_file_lines = textwrap.wrap(
						jupyter_kernel.IPYKERNEL.connection_info.json_str,
						width=width_chars,
					)

					box = subbody.box()
					col = box.column(align=False)
					col.scale_y = 0.5

					for line in wrapped_path_connection_file_lines:
						row = col.row(align=True)
						row.alignment = 'CENTER'
						row.label(text=line)
				else:
					box = subbody.box()
					row = box.row(align=False)
					row.alignment = 'CENTER'
					row.label(text='Kernel Inactive')

		####################
		# - Section: Kernel Networking
		####################
		header, body = layout.panel(
			PanelType.JupyterPanel + '_ipports',
			default_closed=True,
		)
		header.label(text='Kernel IP/Ports')
		if body is not None:  # pyright: ignore[reportUnnecessaryComparison]
			####################
			# - IP Address
			####################
			grid = body.grid_flow(
				row_major=True, columns=2, even_rows=True, even_columns=True
			)

			grid.label(text='Kernel IP')
			grid_section = grid.column()
			grid_section_row = grid_section.row()
			grid_section_row.alignment = 'RIGHT'
			grid_section_row.label(
				text=str(jupyter_kernel.IPYKERNEL.connection_info.ip)
				if jupyter_kernel.IPYKERNEL is not None
				and jupyter_kernel.IPYKERNEL.is_running
				else '',
				icon='QUESTION' if not jupyter_kernel.is_kernel_running() else 'NONE',
			)

			op = grid_section_row.operator(
				OperatorType.CopyKernelInfoToClipboard, icon='COPYDOWN', text=''
			)
			op.value_to_copy = (  # pyright: ignore[reportAttributeAccessIssue]
				str(jupyter_kernel.IPYKERNEL.connection_info.ip)
				if jupyter_kernel.IPYKERNEL is not None
				and jupyter_kernel.IPYKERNEL.is_running
				else ''
			)

			####################
			# - Ports
			####################
			grid = body.grid_flow(
				row_major=True, columns=2, even_rows=True, even_columns=True
			)

			for label, value in zip(
				[
					'Shell',
					'IOPub',
					'Stdin',
					'Control',
					'Heartbeat',
				],
				[
					jupyter_kernel.IPYKERNEL.connection_info.shell_port,
					jupyter_kernel.IPYKERNEL.connection_info.iopub_port,
					jupyter_kernel.IPYKERNEL.connection_info.stdin_port,
					jupyter_kernel.IPYKERNEL.connection_info.control_port,
					jupyter_kernel.IPYKERNEL.connection_info.hb_port,
				]
				if jupyter_kernel.IPYKERNEL is not None
				and jupyter_kernel.IPYKERNEL.is_running
				else 5 * ('',),
				strict=True,
			):
				grid.label(text=label)
				grid_section = grid.column()
				grid_section_row = grid_section.row()
				grid_section_row.alignment = 'RIGHT'
				grid_section_row.label(
					text=str(value),
					icon='QUESTION'
					if not jupyter_kernel.is_kernel_running()
					else 'NONE',
				)
				op = grid_section_row.operator(
					OperatorType.CopyKernelInfoToClipboard, icon='COPYDOWN', text=''
				)
				op.value_to_copy = str(value)  # pyright: ignore[reportAttributeAccessIssue]

		####################
		# - Section: Kernel Security
		####################
		header, body = layout.panel(
			PanelType.JupyterPanel + '_security',
			default_closed=True,
		)
		header.label(text='Kernel Security')
		if body is not None:  # pyright: ignore[reportUnnecessaryComparison]
			####################
			# - Security
			####################
			grid = body.grid_flow(
				row_major=True, columns=2, even_rows=True, even_columns=True
			)

			for label, value in zip(
				[
					'Key',
					'Protocol',
					'Sig. Algo',
				],
				[
					jupyter_kernel.IPYKERNEL.connection_info.key,
					jupyter_kernel.IPYKERNEL.connection_info.transport,
					jupyter_kernel.IPYKERNEL.connection_info.signature_scheme,
				]
				if jupyter_kernel.IPYKERNEL is not None
				and jupyter_kernel.IPYKERNEL.is_running
				else 3 * ('',),
				strict=True,
			):
				grid.label(text=label)
				grid_section = grid.column()
				grid_section_row = grid_section.row()
				grid_section_row.alignment = 'RIGHT'
				grid_section_row.label(
					text=str(value),
					icon='QUESTION'
					if not jupyter_kernel.is_kernel_running()
					else 'NONE',
				)

				# Special Case: Allow Copying Security-Sensitive Values
				## An attacker with access to Blender's memory could get it anyway.
				## Thus, there's no good reason to keep it from the operator.
				if isinstance(value, pyd.SecretStr):
					op = grid_section_row.operator(
						OperatorType.CopyKernelInfoToClipboard, icon='COPYDOWN', text=''
					)
					op.value_to_copy = str(value.get_secret_value())  # pyright: ignore[reportAttributeAccessIssue]
				else:
					op = grid_section_row.operator(
						OperatorType.CopyKernelInfoToClipboard, icon='COPYDOWN', text=''
					)
					op.value_to_copy = str(value)  # pyright: ignore[reportAttributeAccessIssue]


####################
# - Blender Registration
####################
BL_REGISTER = [JupyterPanel]
