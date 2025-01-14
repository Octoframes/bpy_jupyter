import bpy
import platformdirs

from .. import contracts as ct
from ..services import jupyter_kernel as jkern

####################
# - Scene Properties
####################
# Kernel
bpy.types.Scene.jupyter_kernel_type = bpy.props.EnumProperty(
	name='Kernel Type',
	description='The jupyter kernel to launch within Blender',
	items=[
		(
			'IPYKERNEL',
			'IPyKernel',
			'A traditional, well-tested Python notebook kernel',
		),
		# (
		# 'MARIMO',
		# 'Marimo',
		# 'A reactive, modern Python notebook kernel',
		# ),
	],
	default='IPYKERNEL',
)

# Behavior
bpy.types.Scene.jupyter_notebook_dir = bpy.props.StringProperty(
	name='Notebook Root Folder',
	description='The default notebook folder.',
	subtype='DIR_PATH',
	default=platformdirs.user_documents_dir(),
)
bpy.types.Scene.jupyter_launch_browser = bpy.props.BoolProperty(
	name='Auto-Launch Browser?',
	description='Whether to launch a browser automatically when starting the kernel',
	default=True,
)

# Networking
## - See https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
bpy.types.Scene.jupyter_ip = bpy.props.StringProperty(
	name='Jupyter Network IP',
	description='IP address of the Jupyter server',
	default='127.0.0.1',
)

bpy.types.Scene.jupyter_port = bpy.props.IntProperty(
	name='Jupyter Network Port',
	description='Network port of the Jupyter server',
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

	bl_idname = ct.PanelType.JupyterPanel
	bl_label = 'Jupyter Kernel'
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

		# Kernel Panel
		row = layout.row(align=True)
		row.enabled = not jkern.is_kernel_running()
		split = row.split(factor=split_fac, align=True)
		split.alignment = 'RIGHT'
		split.label(text='Kernel')
		split.prop(context.scene, 'jupyter_kernel_type', text='')

		row = layout.row(align=True)
		row.enabled = not jkern.is_kernel_running()
		split = row.split(factor=split_fac, align=True)
		split.alignment = 'RIGHT'
		split.label(text='Root Dir')
		split.prop(context.scene, 'jupyter_notebook_dir', text='')

		header, body = layout.panel(
			'jupyter_network_subpanel',
			default_closed=True,
		)
		header.label(text='Network')
		if body is not None:
			body_row = body.row(align=True)
			body_row.enabled = not jkern.is_kernel_running()
			body_split = body_row.split(factor=split_fac, align=True)
			body_split.alignment = 'RIGHT'
			body_split.label(text='IP')
			body_split.prop(context.scene, 'jupyter_ip', text='')

			body_row = body.row(align=True)
			body_row.enabled = not jkern.is_kernel_running()
			body_split = body_row.split(factor=split_fac, align=True)
			body_split.alignment = 'RIGHT'
			body_split.label(text='Port')
			body_split.prop(context.scene, 'jupyter_port', text='')

		# Operator: Start Kernel
		row = layout.row(align=True)
		row.enabled = not jkern.is_kernel_running()
		split = row.split(factor=0.85, align=True)
		split.alignment = 'RIGHT'
		split.operator(ct.OperatorType.StartJupyterKernel)
		split.prop(
			context.scene,
			'jupyter_launch_browser',
			icon=ct.Icon.LaunchBrowser,
			toggle=True,
			icon_only=True,
		)

		# Operator: Stop Kernel
		row = layout.row(align=True)
		row.operator(ct.OperatorType.StopJupyterKernel)


####################
# - Blender Registration
####################
BL_REGISTER = [JupyterPanel]
BL_HANDLERS: ct.BLHandlers = ct.BLHandlers()
BL_KEYMAP_ITEMS: list[ct.BLKeymapItem] = []
