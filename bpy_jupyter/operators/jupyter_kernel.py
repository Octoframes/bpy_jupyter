"""

Inspired by <https://github.com/cheng-chi/blender_notebook/blob/master/blender_notebook/kernel.py>
"""

import typing as typ

# import asyncio
import bpy

import bpy_jupyter.services.jupyter_kernel as jkern

# JUPYTER_LOOP_TIMER_INTERVAL = 0.016


class StartJupyterKernel(bpy.types.Operator):
	bl_idname = 'bpy_jupyter.start_jupyter_kernel'
	bl_label = 'Start Jupyter'

    #_timer = None

	kernel_type: typ.Literal['IPYKERNEL', 'MARIMO'] | None = None

	@classmethod
	def poll(cls, context: bpy.types.Context) -> bool:
		return jkern.is_kernel_running()

	# def modal(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
	# if event.type == 'TIMER':
	# loop = asyncio.get_event_loop()
	# loop.call_soon(loop.stop)
	# loop.run_forever()

	# return {'PASS_THROUGH'}

	def execute(self, context: bpy.types.Context) -> set[str]:
		# wm = context.window_manager
		# self._timer = wm.event_timer_add(
		# JUPYTER_LOOP_TIMER_INTERVAL, window=context.window
		# )
		# wm.modal_handler_add(self)

		match self.kernel_type:
			case 'IPYKERNEL':
				jkern.start_kernel()  ## TODO: Arg to specify marimo or ipyk

			case 'MARIMO':
				raise NotImplementedError

			## TODO: ERROR on default case

		return {'RUNNING_MODAL'}

		# def cancel(self, context):
		# wm = context.window_manager
		# wm.event_timer_remove(self._timer)
