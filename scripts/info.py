# oscillode
# Copyright (C) 2024 oscillode Project Contributors
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

# blender_maxwell
# Copyright (C) 2024 blender_maxwell Project Contributors
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

"""Informational constants and variables that ease the implementation of scripts external to oscillode.

In general, user-relevant information available here should be mined from `pyproject.toml`, unless it is purely structural.
"""

import tomllib
import typing as typ
from pathlib import Path

import pydantic as pyd
from rich.console import Console

console = Console()

####################
# - Basic
####################
PATH_ROOT = Path(__file__).resolve().parent.parent
with (PATH_ROOT / 'pyproject.toml').open('rb') as f:
	PROJ_SPEC = tomllib.load(f)

REQ_PYTHON_VERSION: str = PROJ_SPEC['project']['requires-python'].replace('~= ', '')


####################
# - Paths
####################
def normalize_path(p_str: str) -> Path:
	"""Convert a project-root-relative '/'-delimited string path to an absolute path.

	This allows for cross-platform path specification, while retaining normalized use of '/' in configuration.

	Args:
		p_str: The '/'-delimited string denoting a path relative to the project root.

	Returns:
		The full absolute path to use when ex. packaging.
	"""
	return PATH_ROOT / Path(*p_str.split('/'))


PATH_PKG = PATH_ROOT / PROJ_SPEC['project']['name']

PATH_DEV = PATH_ROOT / 'dev'
PATH_DEV.mkdir(exist_ok=True)

# Retrieve Build Path
## Extension ZIP files will be placed here after packaging.
PATH_BUILD = normalize_path(PROJ_SPEC['tool']['bl_ext']['packaging']['path_builds'])
PATH_BUILD.mkdir(exist_ok=True)

# Retrieve Wheels Path
## Dependency wheels will be downloaded to here, then copied into the extension packages.
PATH_WHEELS = normalize_path(PROJ_SPEC['tool']['bl_ext']['packaging']['path_wheels'])
PATH_WHEELS.mkdir(exist_ok=True)

# Retrieve Local Cache Path
## During development, files such as logs will be placed here instead of in the extension's user path.
## This is essentially a debugging convenience.
PATH_LOCAL = normalize_path(PROJ_SPEC['tool']['bl_ext']['packaging']['path_local'])
PATH_LOCAL.mkdir(exist_ok=True)

####################
# - Computed Paths
####################
# Compute Current ZIP to Build
## The concrete path to the file that will be packed and installed.
PATH_ZIP = PATH_BUILD / (
	PROJ_SPEC['project']['name'] + '__' + PROJ_SPEC['project']['version'] + '.zip'
)

####################
# - Computed Paths
####################
LogLevel: typ.TypeAlias = int


class InitSettings(pyd.BaseModel):
	"""Model describing addon initialization settings, describing default settings baked into the release."""

	use_log_file: bool
	log_file_path: Path
	log_file_level: LogLevel
	use_log_console: bool
	log_console_level: LogLevel
