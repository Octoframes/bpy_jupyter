"""Provides identifiers for Blender panels defined by this addon."""

import enum

from .addon import NAME as ADDON_NAME

PREFIX = f'{ADDON_NAME.upper()}_PT_'


class PanelType(enum.StrEnum):
	"""Identifiers for addon-defined `bpy.types.Panel`."""

	JupyterPanel = f'{PREFIX}jupyter_panel'
