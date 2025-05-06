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

"""An extension that embeds a Jupyter kernel within Blender.

Attributes:
	BL_REGISTER: All Blender classes that should be registered by `register()`.
"""

from . import operators, panels, preferences
from .services import registration
from .types import BLClass

####################
# - Load and Register Addon
####################
BL_REGISTER: list[type[BLClass]] = [
	*preferences.BL_REGISTER,
	*operators.BL_REGISTER,
	*panels.BL_REGISTER,
]


####################
# - Registration
####################
def register() -> None:
	"""Registers this addon, so that its functionality is available in Blender.

	Notes:
		Called by Blender when enabling this addon.

		Uses `bpy_jupyter.registration.register_classes()` to register all classes collected in `BL_REGISTER`.
	"""
	registration.register_classes(BL_REGISTER)


def unregister() -> None:
	"""Unregisters this addon, so that its functionality is no longer available in Blender.

	Notes:
		Run by Blender when disabling and/or uninstalling the addon.

		Uses `bpy_jupyter.registration.unregister_classes()` to unregister all Blender classes previously registered by this addon.
	"""
	registration.unregister_classes()
