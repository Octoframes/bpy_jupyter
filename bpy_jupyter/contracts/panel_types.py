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

"""Provides identifiers for Blender panels defined by this addon."""

import enum

from .addon import NAME as ADDON_NAME

PREFIX = f'{ADDON_NAME.upper()}_PT_'


class PanelType(enum.StrEnum):
	"""Identifiers for addon-defined `bpy.types.Panel`."""

	JupyterPanel = f'{PREFIX}jupyter_panel'
