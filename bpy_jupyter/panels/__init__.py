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

"""Blender panels that ship with `bpy_jupyter`."""

from functools import reduce

from .. import contracts as ct
from . import jupyter_panel

BL_REGISTER: list[ct.BLClass] = [
	*jupyter_panel.BL_REGISTER,
]
BL_HANDLERS: ct.BLHandlers = reduce(
	lambda a, b: a + b,
	[
		jupyter_panel.BL_HANDLERS,
	],
	ct.BLHandlers(),
)
BL_KEYMAP_ITEMS: list[ct.BLKeymapItem] = [
	*jupyter_panel.BL_KEYMAP_ITEMS,
]
