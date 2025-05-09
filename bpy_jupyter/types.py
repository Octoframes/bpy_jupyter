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

"""Types, enums and constants for use throughout this extension.

Attributes:
	BLClass: A Blender class in `bpy.types` that can be registered.
	BLContextType: A possible value for `bl_context` in `bpy.types.Panel` types.
	PATH_MANIFEST: Path to this addon's `blender_manifest.toml` file.
	MANIFEST: This addon's `blender_manifest.toml` as a dictionary.
	EXT_NAME: Name of this extension.
	EXT_PACKAGE: Value of `__package__` on the top level of this extension.
	PANEL_TYPE_PREFIX: Extension-specific prefix to use for all values in `PanelType`.

References:
	- Deducing Valid `bl_context`: <https://blender.stackexchange.com/questions/73145/when-declaring-a-panel-what-does-the-bl-context-value-need-to-be>
"""

import enum
import tomllib
import typing as typ
from pathlib import Path

import bpy

if __package__ is None:
	msg = "Extension `__package__` is `None`. This shouldn't be possible in a Blender extension."
	raise RuntimeError(msg)

####################
# - Types
####################
BLClass: typ.TypeAlias = (
	bpy.types.Panel
	| bpy.types.UIList
	| bpy.types.Menu
	| bpy.types.Header
	| bpy.types.Operator
	| bpy.types.KeyingSetInfo
	| bpy.types.RenderEngine
	| bpy.types.AssetShelf
	| bpy.types.FileHandler
	| bpy.types.AddonPreferences
)
BLContextType: typ.TypeAlias = typ.Literal[
	'.armature_edit',
	'.curves_sculpt',
	'.grease_pencil_paint',
	'.greasepencil_paint',
	'.greasepencil_sculpt',
	'.greasepencil_vertex',
	'.greasepencil_weight',
	'.imagepaint',
	'.imagepaint_2d',
	'.mesh_edit',
	'.objectmode',
	'.paint_common',
	'.paint_common_2d',
	'.particlemode',
	'.posemode',
	'.sculpt_mode',
	'.uv_sculpt',
	'.vertexpaint',
	'.weightpaint',
	'addons',
	'animation',
	'bone',
	'bone_constraint',
	'collection',
	'constraint',
	'data',
	'editing',
	'experimental',
	'extensions',
	'file_paths',
	'input',
	'interface',
	'keymap',
	'lights',
	'material',
	'modifier',
	'navigation',
	'object',
	'output',
	'particle',
	'physics',
	'render',
	'save_load',
	'scene',
	'shaderfx',
	'system',
	'texture',
	'themes',
	'view_layer',
	'viewport',
	'world',
]

####################
# - Load Manifest
####################
PATH_MANIFEST: Path = Path(__file__).resolve().parent / 'blender_manifest.toml'

with PATH_MANIFEST.open('rb') as f:
	MANIFEST: dict[str, typ.Any] = tomllib.load(f)

EXT_NAME: str = MANIFEST['id']
EXT_PACKAGE: str = __package__

####################
# - Panel Type
####################
PANEL_TYPE_PREFIX = f'{EXT_NAME.upper()}_PT_'


class PanelType(enum.StrEnum):
	"""`bl_idname` values for all addon-defined `bpy.types.Panel`s.

	Attributes:
		JupyterPanel: The `Properties -> Scene` panel that allows managing the embedded Jupyter kernel.
	"""

	JupyterPanel = f'{PANEL_TYPE_PREFIX}jupyter_panel'


####################
# - Operator Type
####################
class OperatorType(enum.StrEnum):
	"""`bl_idname` values for all addon-defined `bpy.types.Operator`s.

	Attributes:
		StartJupyterKernel: Starts an embedded Jupyter kernel, using `bpy_jupyter.services.jupyter_kernel`.

			- Also starts an `asyncio` event loop, using `bpy_jupyter.services.async_event_loop`.
		StopJupyterKernel: Stops the embedded Jupyter kernel, using `bpy_jupyter.services.jupyter_kernel`.

			- Also stops the active `asyncio` event loop, using `bpy_jupyter.services.async_event_loop`.
		CopyKernelInfoToClipboard: Copies some string whose value depends on a running Jupyter kernel, to the system clipboard.
	"""

	StartJupyterKernel = f'{EXT_NAME}.start_jupyter_kernel'
	StopJupyterKernel = f'{EXT_NAME}.stop_jupyter_kernel'
	CopyKernelInfoToClipboard = f'{EXT_NAME}.copy_kernel_info_to_clipboard'
