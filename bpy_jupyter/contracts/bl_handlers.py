"""Declares a structure for aggregating `bpy.app.handlers` callbacks."""

import typing as typ

import bpy
import pydantic as pyd

from ..utils.staticproperty import staticproperty

BLHandler = typ.Callable[[], None]
BLHandlerWithFile = typ.Callable[[str], None]
BLHandlerWithRenderStats = typ.Callable[[typ.Any], None]


class BLHandlers(pyd.BaseModel):
	"""Contains lists of handlers associated with this addon."""

	animation_playback_post: tuple[BLHandler, ...] = ()
	animation_playback_pre: tuple[BLHandler, ...] = ()
	annotation_post: tuple[BLHandler, ...] = ()
	annotation_pre: tuple[BLHandler, ...] = ()
	composite_cancel: tuple[BLHandler, ...] = ()
	composite_post: tuple[BLHandler, ...] = ()
	composite_pre: tuple[BLHandler, ...] = ()
	depsgraph_update_post: tuple[BLHandler, ...] = ()
	depsgraph_update_pre: tuple[BLHandler, ...] = ()
	frame_change_post: tuple[BLHandler, ...] = ()
	frame_change_pre: tuple[BLHandler, ...] = ()
	load_factory_preferences_post: tuple[BLHandler, ...] = ()
	load_factory_startup_post: tuple[BLHandler, ...] = ()
	load_post: tuple[BLHandlerWithFile, ...] = ()
	load_post_fail: tuple[BLHandlerWithFile, ...] = ()
	load_pre: tuple[BLHandlerWithFile, ...] = ()
	object_bake_cancel: tuple[BLHandler, ...] = ()
	object_bake_complete: tuple[BLHandler, ...] = ()
	object_bake_pre: tuple[BLHandler, ...] = ()
	redo_post: tuple[BLHandler, ...] = ()
	redo_pre: tuple[BLHandler, ...] = ()
	render_cancel: tuple[BLHandler, ...] = ()
	render_complete: tuple[BLHandler, ...] = ()
	render_init: tuple[BLHandler, ...] = ()
	render_post: tuple[BLHandler, ...] = ()
	render_pre: tuple[BLHandler, ...] = ()
	render_stats: tuple[BLHandler, ...] = ()
	render_write: tuple[BLHandler, ...] = ()
	save_post: tuple[BLHandlerWithFile, ...] = ()
	save_post_fail: tuple[BLHandlerWithFile, ...] = ()
	save_pre: tuple[BLHandlerWithFile, ...] = ()
	version_update: tuple[BLHandler, ...] = ()
	xr_session_start_pre: tuple[BLHandler, ...] = ()
	## TODO: Verify these type signatures.

	## TODO: A validator to check that all handlers are decorated with bpy.app.handlers.persistent

	####################
	# - Properties
	####################
	@staticproperty  # type: ignore[arg-type]
	def handler_categories() -> tuple[str, ...]:  # type: ignore[misc]
		"""Returns an immutable string sequence of handler categories."""
		return (
			'animation_playback_post',
			'animation_playback_pre',
			'annotation_post',
			'annotation_pre',
			'composite_cancel',
			'composite_post',
			'composite_pre',
			'depsgraph_update_post',
			'depsgraph_update_pre',
			'frame_change_post',
			'frame_change_pre',
			'load_factory_preferences_post',
			'load_factory_startup_post',
			'load_post',
			'load_post_fail',
			'load_pre',
			'object_bake_cancel',
			'object_bake_complete',
			'object_bake_pre',
			'redo_post',
			'redo_pre',
			'render_cancel',
			'render_complete',
			'render_init',
			'render_post',
			'render_pre',
			'render_stats',
		)

	####################
	# - Merging
	####################
	def __add__(self, other: typ.Self) -> typ.Self:
		"""Concatenate two sets of handlers."""
		return self.__class__(
			**{
				hndl_cat: getattr(self, hndl_cat) + getattr(self, hndl_cat)
				for hndl_cat in self.handler_categories
			}
		)

	def register(self) -> None:
		"""Registers all handlers, by-category."""
		for handler_category in BLHandlers.handler_categories:
			for handler in getattr(self, handler_category):
				getattr(bpy.app.handlers, handler_category).append(handler)

	def unregister(self) -> None:
		"""Unregisters only this object's handlers from bpy.app.handlers."""
		for handler_category in BLHandlers.handler_categories:
			for handler in getattr(self, handler_category):
				bpy_handlers = getattr(bpy.app.handlers, handler_category)
				if handler in bpy_handlers:
					bpy_handlers.remove(handler)
