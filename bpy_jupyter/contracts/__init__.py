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

"""Independent constants and types, which represent a kind of 'social contract' governing communication between all components of the addon."""

from . import addon
from .bl import (
	BLClass,
	BLColorRGBA,
	BLEnumElement,
	BLEnumID,
	BLEventType,
	BLEventValue,
	BLIcon,
	BLIconSet,
	BLIDStruct,
	BLImportMethod,
	BLModifierType,
	BLNodeTreeInterfaceID,
	BLOperatorStatus,
	BLPropFlag,
	BLRegionType,
	BLSpaceType,
	PresetName,
	PropName,
	SocketName,
)
from .bl_handlers import BLHandlers
from .bl_keymap import BLKeymapItem
from .icons import Icon
from .operator_types import (
	OperatorType,
)
from .panel_types import (
	PanelType,
)

__all__ = [
	'addon',
	'BLClass',
	'BLColorRGBA',
	'BLEnumElement',
	'BLEnumID',
	'BLEventType',
	'BLEventValue',
	'BLIcon',
	'BLIconSet',
	'BLIDStruct',
	'BLImportMethod',
	'BLKeymapItem',
	'BLModifierType',
	'BLNodeTreeInterfaceID',
	'BLOperatorStatus',
	'BLPropFlag',
	'BLRegionType',
	'BLSpaceType',
	'KeymapItemDef',
	'ManagedObjName',
	'PresetName',
	'PropName',
	'SocketName',
	'BLHandlers',
	'Icon',
	'BLInstance',
	'InstanceID',
	'NodeTreeType',
	'OperatorType',
	'PanelType',
]
