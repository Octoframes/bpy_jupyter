"""A lightweight, `rich`-based approach to logging that is isolated from other extensions that may used the Python stdlib `logging` module."""

import logging
import typing as typ
from pathlib import Path

import rich.console
import rich.logging
import rich.traceback

from .. import contracts as ct
from ..services import init_settings

LogLevel: typ.TypeAlias = int


####################
# - Configuration
####################
STREAM_LOG_FORMAT = 11 * ' ' + '%(levelname)-8s %(message)s (%(name)s)'
FILE_LOG_FORMAT = STREAM_LOG_FORMAT

OUTPUT_CONSOLE = rich.console.Console(
	color_system='truecolor',
)
ERROR_CONSOLE = rich.console.Console(
	color_system='truecolor',
	stderr=True,
)

ADDON_LOGGER_NAME = f'blext-{ct.addon.NAME}'
ADDON_LOGGER: logging.Logger = logging.getLogger(ADDON_LOGGER_NAME)

rich.traceback.install(show_locals=True, console=ERROR_CONSOLE)


####################
# - Logger Access
####################
def all_addon_loggers() -> set[logging.Logger]:
	"""Retrieve all loggers currently declared by this addon.

	These loggers are all children of `ADDON_LOGGER`, essentially.
	This allows for name-isolation from other Blender extensions, as well as easy cleanup.

	Returns:
		Set of all loggers declared by this addon.
	"""
	return {
		logging.getLogger(name)
		for name in logging.root.manager.loggerDict
		if name.startswith(ADDON_LOGGER_NAME)
	}
	## TODO: Python 3.12 has a .getChildren() method that also returns sets.


####################
# - Logging Handlers
####################
def console_handler(level: LogLevel) -> rich.logging.RichHandler:
	"""A logging handler that prints messages to the console.

	Parameters:
		level: The log levels (debug, info, etc.) to print.

	Returns:
		The logging handler, which can be added to a logger.
	"""
	rich_formatter = logging.Formatter(
		'%(message)s',
		datefmt='[%X]',
	)
	rich_handler = rich.logging.RichHandler(
		level=level,
		console=ERROR_CONSOLE,
		rich_tracebacks=True,
	)
	rich_handler.setFormatter(rich_formatter)
	return rich_handler


def file_handler(path_log_file: Path, level: LogLevel) -> rich.logging.RichHandler:
	"""A logging handler that prints messages to a file.

	Parameters:
		path_log_file: The path to the log file.
		level: The log levels (debug, info, etc.) to append to the file.

	Returns:
		The logging handler, which can be added to a logger.
	"""
	file_formatter = logging.Formatter(FILE_LOG_FORMAT)
	file_handler = logging.FileHandler(path_log_file)
	file_handler.setFormatter(file_formatter)
	file_handler.setLevel(level)
	return file_handler


####################
# - Logger Setup
####################
def get(module_name: str) -> logging.Logger:
	"""Retrieve and/or create a logger corresponding to a module name.

	Warnings:
		MUST be used as `logger.get(__name__)`.

	Parameters:
		module_name: The `__name__` of the module to return a logger for.
	"""
	log = ADDON_LOGGER.getChild(module_name)

	# Setup Logger from Init Settings or Addon Preferences
	## - We prefer addon preferences, but they may not be setup yet.
	## - Once setup, the preferences may decide to re-configure all the loggers.
	addon_prefs = ct.addon.prefs()
	if addon_prefs is None:
		use_log_file = init_settings.INIT_SETTINGS.use_log_file
		log_file_path = init_settings.INIT_SETTINGS.log_file_path
		log_file_level = init_settings.INIT_SETTINGS.log_file_level
		use_log_console = init_settings.INIT_SETTINGS.use_log_console
		log_console_level = init_settings.INIT_SETTINGS.log_console_level

		update_logger(
			console_handler,
			file_handler,
			log,
			file_path=log_file_path if use_log_file else None,
			file_level=log_file_level,
			console_level=log_console_level if use_log_console else None,
		)
	else:
		addon_prefs.setup_logger(log)

	return log


####################
# - Logger Update
####################
def _init_logger(logger: logging.Logger) -> None:
	"""Prepare a logger for handlers to be added, ensuring normalized semantics for all loggers.

	- Messages should not propagate to the root logger, causing double-messages.
	- Mesages should not filter by level; this is the job of the handlers.
	- No handlers must be set.

	Args:
		logger: The logger to prepare.
	"""
	# DO NOT Propagate to Root Logger
	## - This looks like 'double messages'
	## - See SO/6729268/log-messages-appearing-twice-with-python-logging
	logger.propagate = False

	# Let All Messages Through
	## - The individual handlers perform appropriate filtering.
	logger.setLevel(logging.NOTSET)

	if logger.handlers:
		logger.handlers.clear()


def update_logger(
	cb_console_handler: typ.Callable[[LogLevel], logging.Handler],
	cb_file_handler: typ.Callable[[Path, LogLevel], logging.Handler],
	logger: logging.Logger,
	console_level: LogLevel | None,
	file_path: Path | None,
	file_level: LogLevel,
) -> None:
	"""Configures a single logger with given console and file handlers, individualizing the log level that triggers it.

	This is a lower-level function - generally, modules that want to use a well-configured logger will use the `get()` function, which retrieves the parameters for this function from the addon preferences.
	This function is used by the higher-level log setup.

	Parameters:
		cb_console_handler: A function that takes a log level threshold (inclusive), and returns a logging handler to a console-printer.
		cb_file_handler: A function that takes a log level threshold (inclusive), and returns a logging handler to a file-printer.
		logger: The logger to configure.
		console_level: The log level threshold to print to the console.
			None deactivates file logging.
		path_log_file: The path to the log file.
			None deactivates file logging.
		file_level: The log level threshold to print to the log file.
	"""
	# Initialize Logger
	_init_logger(logger)

	# Add Console Logging Handler
	if console_level is not None:
		logger.addHandler(cb_console_handler(console_level))

	# Add File Logging Handler
	if file_path is not None:
		logger.addHandler(cb_file_handler(file_path, file_level))
