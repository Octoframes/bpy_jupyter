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

"""Blender operators that ship with `bpy_jupyter`."""

from . import copy_jupy_url_to_clip, start_jupyter_kernel, stop_jupyter_kernel

BL_REGISTER = [
	*start_jupyter_kernel.BL_REGISTER,
	*stop_jupyter_kernel.BL_REGISTER,
	*copy_jupy_url_to_clip.BL_REGISTER,
]
