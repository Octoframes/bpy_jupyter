"""Explicit type annotations for Blender objects, making it easier to guarantee correctness in communications with Blender."""

import typing as typ

import bpy

####################
# - Blender Strings
####################
BLEnumID: typ.TypeAlias = str
SocketName: typ.TypeAlias = str
PropName: typ.TypeAlias = str

####################
# - Blender Enums
####################
BLImportMethod: typ.TypeAlias = typ.Literal['append', 'link']
BLModifierType: typ.TypeAlias = typ.Literal['NODES', 'ARRAY']
BLNodeTreeInterfaceID: typ.TypeAlias = str

BLIcon: typ.TypeAlias = str
BLIconSet: frozenset[BLIcon] = frozenset(
	bpy.types.UILayout.bl_rna.functions['prop'].parameters['icon'].enum_items.keys()
)

BLEnumElement = tuple[BLEnumID, str, str, BLIcon, int]

####################
# - Blender Structs
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
)
BLIDStruct: typ.TypeAlias = (
	bpy.types.Action
	| bpy.types.Armature
	| bpy.types.Brush
	| bpy.types.CacheFile
	| bpy.types.Camera
	| bpy.types.Collection
	| bpy.types.Curve
	| bpy.types.Curves
	| bpy.types.FreestyleLineStyle
	| bpy.types.GreasePencil
	| bpy.types.Image
	| bpy.types.Key
	| bpy.types.Lattice
	| bpy.types.Library
	| bpy.types.Light
	| bpy.types.LightProbe
	| bpy.types.Mask
	| bpy.types.Material
	| bpy.types.Mesh
	| bpy.types.MetaBall
	| bpy.types.MovieClip
	| bpy.types.NodeTree
	| bpy.types.Object
	| bpy.types.PaintCurve
	| bpy.types.Palette
	| bpy.types.ParticleSettings
	| bpy.types.PointCloud
	| bpy.types.Scene
	| bpy.types.Screen
	| bpy.types.Sound
	| bpy.types.Speaker
	| bpy.types.Text
	| bpy.types.Texture
	| bpy.types.VectorFont
	| bpy.types.Volume
	| bpy.types.WindowManager
	| bpy.types.WorkSpace
	| bpy.types.World
)
BLPropFlag: typ.TypeAlias = typ.Literal[
	'HIDDEN',
	'SKIP_SAVE',
	'SKIP_PRESET',
	'ANIMATABLE',
	'LIBRARY_EDITABLE',
	'PROPORTIONAL',
	'TEXTEDIT_UPDATE',
	'OUTPUT_PATH',
]
BLColorRGBA = tuple[float, float, float, float]


####################
# - Operators
####################
BLRegionType: typ.TypeAlias = typ.Literal[
	'WINDOW',
	'HEADER',
	'CHANNELS',
	'TEMPORARY',
	'UI',
	'TOOLS',
	'TOOL_PROPS',
	'ASSET_SHELF',
	'ASSET_SHELF_HEADER',
	'PREVIEW',
	'HUD',
	'NAVIGATION_BAR',
	'EXECUTE',
	'FOOTER',
	'TOOL_HEADER',
	'XR',
]
BLSpaceType: typ.TypeAlias = typ.Literal[
	'EMPTY',
	'VIEW_3D',
	'IMAGE_EDITOR',
	'NODE_EDITOR',
	'SEQUENCE_EDITOR',
	'CLIP_EDITOR',
	'DOPESHEET_EDITOR',
	'GRAPH_EDITOR',
	'NLA_EDITOR',
	'TEXT_EDITOR',
	'CONSOLE',
	'INFO',
	'TOPBAR',
	'STATUSBAR',
	'OUTLINER',
	'PROPERTIES',
	'FILE_BROWSER',
	'SPREADSHEET',
	'PREFERENCES',
]
BLOperatorStatus: typ.TypeAlias = set[
	typ.Literal['RUNNING_MODAL', 'CANCELLED', 'FINISHED', 'PASS_THROUGH', 'INTERFACE']
]

####################
# - Operators
####################
## TODO: Write the rest in.
BLEventType: typ.TypeAlias = typ.Literal[
	'NONE',
	'LEFTMOUSE',
	'MIDDLEMOUSE',
	'RIGHTMOUSE',
	'BUTTON4MOUSE',
	'BUTTON5MOUSE',
	'BUTTON6MOUSE',
	'BUTTON7MOUSE',
	'PEN',
	'ERASOR',
	'MOUSEMOVE',
	'INBETWEEN_MOUSEMOVE',
	'TRACKPADPAN',
	'TRACKPADZOOM',
	'MOUSEROTATE',
	'MOUSESMARTZOOM',
	'WHEELUPMOUSE',
	'WHEELDOWNMOUSE',
	'WHEELINMOUSE',
	'WHEELOUTMOUSE',
	'A',
	'B',
	'C',
	'D',
	'E',
	'F',
	'G',
	'H',
	'I',
	'J',
	'K',
	'L',
	'M',
	'N',
	'O',
	'P',
	'Q',
	'R',
	'S',
	'T',
	'U',
	'V',
	'W',
	'X',
	'Y',
	'Z',
	'ZERO',
	'ONE',
	'TWO',
	'THREE',
	'FOUR',
	'FIVE',
	'SIX',
	'SEVEN',
	'EIGHT',
	'NINE',
	'LEFT_CTRL',
	'LEFT_ALT',
	'LEFT_SHIFT',
	'RIGHT_ALT',
	'RIGHT_CTRL',
	'RIGHT_SHIFT',
	'ESC',
	'TAB',
	'RET',  ## Enter
	'SPACE',
	'LINE_FEED',
	'BACK_SPACE',
	'DEL',
	'SEMI_COLON',
	'PERIOD',
	'COMMA',
	'QUOTE',
	'ACCENT_GRAVE',
	'MINUS',
	'PLUS',
	'SLASH',
	'BACK_SLASH',
	'EQUAL',
	'LEFT_BRACKET',
	'RIGHT_BRACKET',
	'LEFT_ARROW',
	'DOWN_ARROW',
	'RIGHT_ARROW',
	'UP_ARROW',
	'NUMPAD_0',
	'NUMPAD_1',
	'NUMPAD_2',
	'NUMPAD_3',
	'NUMPAD_4',
	'NUMPAD_5',
	'NUMPAD_6',
	'NUMPAD_7',
	'NUMPAD_8',
	'NUMPAD_9',
	'NUMPAD_PERIOD',
	'NUMPAD_SLASH',
	'NUMPAD_ASTERIX',
	'NUMPAD_MINUS',
	'NUMPAD_PLUS',
	'NUMPAD_ENTER',
	'F1',
	'F2',
	'F3',
	'F4',
	'F5',
	'F6',
	'F7',
	'F8',
	'F9',
	'F10',
	'F11',
	'F12',
	'PAUSE',
	'INSERT',
	'HOME',
	'PAGE_UP',
	'PAGE_DOWN',
	'END',
	'MEDIA_PLAY',
	'MEDIA_STOP',
	'MEDIA_FIRST',
	'MEDIA_LAST',
]
BLEventValue: typ.TypeAlias = typ.Literal[
	'ANY',
	'PRESS',
	'RELEASE',
	'CLICK',
	'DOUBLE_CLICK',
	'CLICK_DRAG',
	'NOTHING',
]

####################
# - Blender Strings
####################
PresetName = str
