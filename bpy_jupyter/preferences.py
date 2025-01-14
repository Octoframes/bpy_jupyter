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

"""Addon preferences, encapsulating the various global modifications that the user may make to how this addon functions."""

import logging
from pathlib import Path

import bpy

from .services.init_settings import INIT_SETTINGS
from .utils import logger

log = logger.get(__name__)


####################
# - Constants
####################
LOG_LEVEL_MAP: dict[str, logger.LogLevel] = {
	'DEBUG': logging.DEBUG,
	'INFO': logging.INFO,
	'WARNING': logging.WARNING,
	'ERROR': logging.ERROR,
	'CRITICAL': logging.CRITICAL,
}


####################
# - Preferences
####################
class BPYJupyterAddonPrefs(bpy.types.AddonPreferences):
	"""Manages user preferences and settings for the Blender Maxwell addon.

	Unfortunately, many of the niceities based on dependencies (ex. `bl_cache.BLField`) aren't available here.


	Attributes:
		bl_idname: Matches `ct.addon.NAME`.
		use_default_pydeps_path: Whether to use the default PyDeps path
	"""

	bl_idname = __package__

	####################
	# - Properties
	####################
	# Logging
	## File Logging
	use_log_file: bpy.props.BoolProperty(  # type: ignore
		name='Log to File',
		description='Whether to use a file for addon logging',
		default=INIT_SETTINGS.use_log_file,
		update=lambda self, _: self.on_addon_logging_changed(),
	)
	log_level_file: bpy.props.EnumProperty(  # type: ignore
		name='File Log Level',
		description='Level of addon logging to expose in the file',
		items=[
			('DEBUG', 'Debug', 'Debug'),
			('INFO', 'Info', 'Info'),
			('WARNING', 'Warning', 'Warning'),
			('ERROR', 'Error', 'Error'),
			('CRITICAL', 'Critical', 'Critical'),
		],
		default=INIT_SETTINGS.log_file_level,
		update=lambda self, _: self.on_addon_logging_changed(),
	)

	bl__log_file_path: bpy.props.StringProperty(  # type: ignore
		name='Log Path',
		description='Path to the Addon Log File',
		subtype='FILE_PATH',
		default=str(INIT_SETTINGS.log_file_path),
		update=lambda self, _: self.on_addon_logging_changed(),
	)

	@property
	def log_file_path(self) -> Path:
		"""Retrieve the configured file-logging path as a `pathlib.Path`."""
		return Path(bpy.path.abspath(self.bl__log_file_path))

	@log_file_path.setter
	def log_file_path(self, path: Path) -> None:
		"""Set the configured file-logging path as a `pathlib.Path`."""
		self.bl__log_file_path = str(path.resolve())

	## Console Logging
	use_log_console: bpy.props.BoolProperty(  # type: ignore
		name='Log to Console',
		description='Whether to use the console for addon logging',
		default=INIT_SETTINGS.use_log_console,
		update=lambda self, _: self.on_addon_logging_changed(),
	)
	log_level_console: bpy.props.EnumProperty(  # type: ignore
		name='Console Log Level',
		description='Level of addon logging to expose in the console',
		items=[
			('DEBUG', 'Debug', 'Debug'),
			('INFO', 'Info', 'Info'),
			('WARNING', 'Warning', 'Warning'),
			('ERROR', 'Error', 'Error'),
			('CRITICAL', 'Critical', 'Critical'),
		],
		default=INIT_SETTINGS.log_console_level,
		update=lambda self, _: self.on_addon_logging_changed(),
	)

	####################
	# - Events: Properties Changed
	####################
	def setup_logger(self, _logger: logging.Logger) -> None:
		"""Setup a logger using the settings declared in the addon preferences.

		Args:
			_logger: The logger to configure using settings in the addon preferences.
		"""
		logger.update_logger(
			logger.console_handler,
			logger.file_handler,
			_logger,
			file_path=self.log_file_path if self.use_log_file else None,
			file_level=LOG_LEVEL_MAP[self.log_level_file],
			console_level=LOG_LEVEL_MAP[self.log_level_console]
			if self.use_log_console
			else None,
		)

	def on_addon_logging_changed(self) -> None:
		"""Called to reconfigure all loggers to match newly-altered addon preferences.

		This causes ex. changes to desired console log level to immediately be applied, but only the this addon's loggers.

		Parameters:
			single_logger_to_setup: When set, only this logger will be setup.
				Otherwise, **all addon loggers will be setup**.
		"""
		log.info('Reconfiguring Loggers')
		for _logger in logger.all_addon_loggers():
			self.setup_logger(_logger)

		log.info('Loggers Reconfigured')

	####################
	# - UI
	####################
	def draw(self, _: bpy.types.Context) -> None:
		"""Draw the addon preferences within its panel in Blender's preferences.

		Notes:
			Run by Blender when this addon's preferences need to be displayed.

		Parameters:
			context: The Blender context object.
		"""
		layout = self.layout

		####################
		# - Logging
		####################
		# Box w/Split: Log Level
		box = layout.box()
		row = box.row()
		row.alignment = 'CENTER'
		row.label(text='Logging')
		split = box.split(factor=0.5)

		## Split Col: Console Logging
		col = split.column()
		row = col.row()
		row.prop(self, 'use_log_console', toggle=True)

		row = col.row()
		row.enabled = self.use_log_console
		row.prop(self, 'log_level_console')

		## Split Col: File Logging
		col = split.column()
		row = col.row()
		row.prop(self, 'use_log_file', toggle=True)

		row = col.row()
		row.enabled = self.use_log_file
		row.prop(self, 'bl__log_file_path')

		row = col.row()
		row.enabled = self.use_log_file
		row.prop(self, 'log_level_file')


####################
# - Blender Registration
####################
BL_REGISTER = [
	BPYJupyterAddonPrefs,
]
