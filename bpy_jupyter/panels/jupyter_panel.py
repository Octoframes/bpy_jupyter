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
import platformdirs

from ..services import jupyter_kernel
from ..types import Icon, OperatorType, PanelType

####################
# - Scene Properties
####################
# Behavior
bpy.types.Scene.jupyter_notebook_dir = bpy.props.StringProperty(
	name='Notebook Root Folder',
	description='The top-level folder in which the Jupyter server can find and store notebooks.',
	subtype='DIR_PATH',
	default=platformdirs.user_desktop_dir(),
)
bpy.types.Scene.jupyter_launch_browser = bpy.props.BoolProperty(
	name='Auto-Launch Browser?',
	description='Whether to launch the default browser automatically, pointing to Jupyter Lab, when starting Jupyter.',
	default=True,
)

# Networking
## - See https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
bpy.types.Scene.jupyter_ip = bpy.props.StringProperty(
	name='Jupyter Network IP',
	description='IPv4 address of the launched Jupyter server',
	default='127.0.0.1',
)

bpy.types.Scene.jupyter_port = bpy.props.IntProperty(
	name='Jupyter Network Port',
	description='Network port of the launched Jupyter server',
	min=1024,
	max=49151,
	default=10462,
)


####################
# - Scene Properties
####################
class JupyterPanel(bpy.types.Panel):
	"""'Controls the Jupyter kernel launched using Blender."""

	## TODO: Provide an option that forces appending? So that users can modify from a baseline. Just watch out - dealing with overlaps isn't trivial.

	bl_idname = PanelType.JupyterPanel
	bl_label = 'Jupyter Notebooks'
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = 'scene'

	@classmethod
	def poll(cls, _: bpy.types.Context) -> bool:
		"""Always show Jupyter panel in Scene properties.

		Notes:
			Run by Blender when trying to show a panel.

		Returns:
			Whether the panel can show.
		"""
		return True

	def draw(self, context: bpy.types.Context) -> None:
		"""Draw the Jupyter panel w/options.

		Notes:
			Run by Blender when the panel needs to be displayed.

		Parameters:
			context: The Blender context object.
				Must contain `context.window_manager` and `context.workspace`.
		"""
		split_fac = 0.25
		layout = self.layout

		####################
		# - Section: Stop/Start Kernel
		####################
		# Operator: Start Kernel
		row = layout.row(align=True)
		row.enabled = not jupyter_kernel.is_kernel_running()
		split = row.split(factor=0.85, align=True)
		split.alignment = 'RIGHT'
		split.operator(OperatorType.StartJupyterKernel)
		split.prop(
			context.scene,
			'jupyter_launch_browser',
			icon=Icon.LaunchBrowser,
			toggle=True,
			icon_only=True,
		)

		# Operator: Stop Kernel
		row = layout.row(align=True)
		row.operator(OperatorType.StopJupyterKernel)

		####################
		# - Section: Basic Options
		####################
		header, body = layout.panel(
			'jupyter_basic_options_subpanel',
			default_closed=False,
		)
		header.label(text='Basic Options')
		if body is not None:
			row = body.row(align=True)
			row.enabled = not jupyter_kernel.is_kernel_running()
			split = row.split(factor=split_fac, align=True)
			split.alignment = 'RIGHT'
			split.label(text='Notebook Dir')
			split.prop(context.scene, 'jupyter_notebook_dir', text='')

		####################
		# - Section: Network Options
		####################
		header, body = layout.panel(
			'jupyter_network_options_subpanel',
			default_closed=True,
		)
		header.label(text='Network Options')
		if body is not None:
			body_row = body.row(align=True)
			body_row.enabled = not jupyter_kernel.is_kernel_running()
			body_split = body_row.split(factor=split_fac, align=True)
			body_split.alignment = 'RIGHT'
			body_split.label(text='IPv4')
			body_split.prop(context.scene, 'jupyter_ip', text='')

			body_row = body.row(align=True)
			body_row.enabled = not jupyter_kernel.is_kernel_running()
			body_split = body_row.split(factor=split_fac, align=True)
			body_split.alignment = 'RIGHT'
			body_split.label(text='Port')
			body_split.prop(context.scene, 'jupyter_port', text='')

		####################
		# - Section: Copyable URLs
		####################
		header, body = layout.panel(
			'jupyter_copy_urls_subpanel',
			default_closed=False,
		)
		header.label(text='URLs')
		if body is not None:
			# Label
			row = body.row(align=False)
			row.alignment = 'CENTER'
			row.label(text='Copy URLs to Clipboard:')

			# Operators
			row = body.row(align=False)

			op = row.operator(OperatorType.CopyJupyURLToClip, text='Lab URL')
			op.url_type = 'LAB'

			op = row.operator(OperatorType.CopyJupyURLToClip, text='API URL')
			op.url_type = 'API'


####################
# - Blender Registration
####################
BL_REGISTER = [JupyterPanel]
