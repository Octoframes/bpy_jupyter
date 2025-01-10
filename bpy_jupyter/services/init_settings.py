"""Authoritative definition and storage of "Initialization Settings", which provide out-of-the-box defaults for settings relevant for ex. debugging.

These settings are transported via a special TOML file that is packed into the extension zip-file when packaging for release.
"""

import logging
import tomllib
import typing as typ
from pathlib import Path

import pydantic as pyd

####################
# - Constants
####################
PATH_ROOT = Path(__file__).resolve().parent.parent
INIT_SETTINGS_FILENAME = 'init_settings.toml'


####################
# - Types
####################
LogLevel: typ.TypeAlias = int
StrLogLevel: typ.TypeAlias = typ.Literal[
	'DEBUG',
	'INFO',
	'WARNING',
	'ERROR',
	'CRITICAL',
]


def str_to_loglevel(obj: typ.Any) -> LogLevel | typ.Any:
	if isinstance(obj, str) and obj in STR_LOG_LEVEL:
		return STR_LOG_LEVEL[obj]
	return obj


class InitSettings(pyd.BaseModel):
	"""Model describing addon initialization settings, describing default settings baked into the release.

	Each parameter

	"""

	use_log_file: bool
	log_file_path: Path
	log_file_level: StrLogLevel

	use_log_console: bool
	log_console_level: StrLogLevel


####################
# - Init Settings Management
####################
with (PATH_ROOT / INIT_SETTINGS_FILENAME).open('rb') as f:
	INIT_SETTINGS: InitSettings = InitSettings(**tomllib.load(f))
