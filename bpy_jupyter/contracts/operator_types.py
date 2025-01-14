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

"""Provides identifiers for Blender operators defined by this addon."""

import enum

from .addon import NAME as ADDON_NAME


class OperatorType(enum.StrEnum):
	"""Identifiers for addon-defined `bpy.types.Operator`."""

	StartJupyterKernel = f'{ADDON_NAME}.start_jupyter_kernel'
	StopJupyterKernel = f'{ADDON_NAME}.stop_jupyter_kernel'
