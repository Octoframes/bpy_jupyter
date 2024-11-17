import bpy


class JupyterPanel(bpy.types.Panel):
	## TODO: Provide an option that forces appending? So that users can modify from a baseline. Just watch out - dealing with overlaps isn't trivial.

	bl_idname = 'bpy_jupyter.node_asset_panel'
	bl_label = 'Node GeoNodes Asset Panel'
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = 'scene'

	kernel_type: bpy.props.EnumProperty(  # type: ignore
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
		# update=lambda self, _: self.on_addon_logging_changed(),
	)

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
		layout.prop(self, 'kernel_type')

		# Operator
		op = layout.operator('bpy_jupyter.start_jupyter_kernel')
		op.kernel_type = self.kernel_type
