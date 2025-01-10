import bpy

from .. import contracts as ct


bpy.types.Scene.jupyter_kernel_type = bpy.props.EnumProperty(
	name='Kernel Type',
	description='The jupyter kernel to launch within Blender',
	items=[
		(
			'IPYKERNEL',
			'IPyKernel',
			'A traditional, well-tested Python notebook kernel',
		),
		(
			'MARIMO',
			'Marimo',
			'A reactive, modern Python notebook kernel',
		),
	],
	default='IPYKERNEL',
)


class JupyterPanel(bpy.types.Panel):
	"""'Controls the Jupyter kernel launched using Blender."""

	## TODO: Provide an option that forces appending? So that users can modify from a baseline. Just watch out - dealing with overlaps isn't trivial.

	bl_idname = ct.PanelType.JupyterPanel
	bl_label = 'Jupyter Kernel'
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = 'scene'

	@classmethod
	def poll(cls, context: bpy.types.Context) -> bool:
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
		layout = self.layout

		# Properties
		layout.prop(context.scene, 'jupyter_kernel_type')

		# Operator
		op = layout.operator('bpy_jupyter.start_jupyter_kernel')
		op.kernel_type = context.scene.jupyter_kernel_type


####################
# - Blender Registration
####################
BL_REGISTER = [JupyterPanel]
BL_HANDLERS: ct.BLHandlers = ct.BLHandlers()
BL_KEYMAP_ITEMS: list[ct.BLKeymapItem] = []
