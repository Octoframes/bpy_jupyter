"""Structural constants defining the makeup of this Blender extension project.

Use of `pyproject.toml` should always be preferred for customizing the extension itself.
The developer should, therefore, not need to modify this file.

Attributes:
	PATH_ROOT: Path to the project root.
	PATH_PROJ_SPEC: Path to the project's `pyproject.toml` file.
	PATH_DEV: "Development files" not checked into `git`.
		This is often an ideal location for volatile local ex. caches, targets, etc. .
	PATH_WHEELS: Target path for downloaded `.wheel` files.
	PATH_BUILD: Target path for built extension `.zip` file(s).
	PATH_LOCAL: During development, this path is used by the extension instead of a global user folder.
		This is ideal for analyzing logs and other artifacts for debugging.
"""

from pathlib import Path

from blext import spec

####################
# - Specification
####################
PATH_ROOT: Path = Path(__file__).resolve().parent.parent
PATH_PROJ_SPEC: Path = PATH_ROOT / 'pyproject.toml'


####################
# - Paths
####################
# Dev Path
PATH_DEV: Path = PATH_ROOT / 'dev'
PATH_DEV.mkdir(exist_ok=True)

# Wheels Path
PATH_WHEELS: Path = PATH_DEV / 'wheels'
PATH_WHEELS.mkdir(exist_ok=True)

# Build Path
PATH_BUILD: Path = PATH_DEV / 'build'
PATH_BUILD.mkdir(exist_ok=True)

# Local Path
PATH_LOCAL: Path = PATH_DEV / 'local'
PATH_LOCAL.mkdir(exist_ok=True)
