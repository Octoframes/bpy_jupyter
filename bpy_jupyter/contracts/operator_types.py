"""Provides identifiers for Blender operators defined by this addon."""

import enum

from .addon import NAME as ADDON_NAME


class OperatorType(enum.StrEnum):
	"""Identifiers for addon-defined `bpy.types.Operator`."""

	StartJupyterKernel = f'{ADDON_NAME}.start_jupyter_kernel'
