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

"""A visual DSL for electromagnetic simulation design and analysis implemented as a Blender node editor."""

from . import operators, panels, preferences, registration

####################
# - Load and Register Addon
####################
BL_REGISTER = [
	*preferences.BL_REGISTER,
	*operators.BL_REGISTER,
	*panels.BL_REGISTER,
]


####################
# - Registration
####################
def register() -> None:
	"""Implements addon registration in a way that respects the availability of addon preferences and loggers.

	Notes:
		Called by Blender when enabling the addon.

	Raises:
		RuntimeError: If addon preferences fail to register.
	"""
	registration.register_classes(BL_REGISTER)


def unregister() -> None:
	"""Unregisters anything that was registered by the addon.

	Notes:
		Run by Blender when disabling and/or uninstalling the addon.

		This doesn't clean `sys.modules`.
		We rely on the hope that Blender has extension-extension module isolation.
	"""
	registration.unregister_classes()
