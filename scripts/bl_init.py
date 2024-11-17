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

import sys
from pathlib import Path

import bpy

PATH_SCRIPT = str(Path(__file__).resolve().parent)
sys.path.insert(0, str(PATH_SCRIPT))
import info  # noqa: E402
import pack  # noqa: E402

sys.path.remove(str(PATH_SCRIPT))


####################
# - Main
####################
if __name__ == '__main__':
	pass
	# Uninstall Old Extension
	# if any(addon_name.endwith(info.ADDON_NAME) and addon_name.startswith('bl_ext.') for addon_name in bpy.context.preferences.addons.keys()):
	# bpy.ops.extensions.package_uninstall(pkg_id=info.ADDON_NAME)

	# Install New Extension
	# with pack.zipped_addon(
	# info.PATH_ADDON_PKG,
	# info.PATH_ADDON_ZIP,
	# info.PATH_ROOT / 'pyproject.toml',
	# info.PATH_ROOT / 'requirements.lock',
	# initial_log_level=info.BOOTSTRAP_LOG_LEVEL,
	# ) as path_zipped:
# bpy.ops.extensions.package_install_files(
# filepath=path_zipped,
# enable_on_install=True,
#
# )
