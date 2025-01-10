import json
import tomllib
import typing as typ
from pathlib import Path

import pydantic as pyd
import tomli_w

####################
# - Path Mangling
####################
PATH_ROOT: Path = Path(__file__).resolve().parent.parent


def parse_spec_path(p_str: str) -> Path:
	"""Convert a project-root-relative '/'-delimited string path to an absolute path.

	This allows for cross-platform path specification, while retaining normalized use of '/' in configuration.

	Args:
		p_str: The '/'-delimited string denoting a path relative to the project root.

	Returns:
		The full absolute path to use when ex. packaging.
	"""
	return PATH_ROOT / Path(*p_str.split('/'))


####################
# - Types
####################
LogLevel: typ.TypeAlias = int
StrLogLevel: typ.TypeAlias = typ.Literal[
	'DEBUG',
	'INFO',
	'WARNING',
	'ERROR',
	'CRITICAL',
]


# class BLExtSpec(pyd.BaseModel, frozen=True):  ## TODO: FrozenDict
class BLExtSpec(pyd.BaseModel):
	"""Blender extension information, parsed from the `[tool.bl_ext]` section of a `pyproject.toml`.

	For inspiration, see the following links:
	- <https://docs.blender.org/manual/en/4.2/extensions/getting_started.html>
	- <https://packaging.python.org/en/latest/guides/writing-pyproject-toml>

	Attributes:
		init_settings_filename: Must be `init_settings.toml`.
		use_path_local: Whether to use a local path, instead of a global system path.
			Useful for debugging during development.
		use_log_file: Whether the extension should default to the use of file logging.
		log_file_path: The path to the file log (if enabled).
		log_file_level: The file log level to use (if enabled).
		use_log_console: Whether the extension should default to the use of console logging.
		log_console_level: The console log level to use (if enabled).
		schema_version: Must be 1.0.0.
		id: Unique identifying name of the extension.
		name: Pretty, user-facing name of the extension.
		version: The version of the extension.
		tagline: Short description of the extension.
		maintainer: Primary maintainer of the extension (name and email).
		type: Type of extension.
			Currently, only `add-on` is supported.
		blender_version_min: The minimum version of Blender that this extension supports.
		blender_version_max: The maximum version of Blender that this extension supports.
		wheels_path: Base path for local management of wheels.
		wheels: Relative paths to wheels distributed with this extension.
			These should be installed by Blender alongside the extension.
			See <https://docs.blender.org/manual/en/dev/extensions/python_wheels.html> for more information.
		permissions: Permissions required by the extension.
		tags: Tags for categorizing the extension.
		license: License of the extension's source code.
		copyright: Copyright declaration of the extension.
		website: Homepage of the extension.
	"""

	req_python_version: str

	####################
	# - Init Settings
	####################
	init_settings_filename: typ.Literal['init_settings.toml'] = 'init_settings.toml'

	# Path Locality
	use_path_local: bool
	path_local: Path | None = None

	# File Logging
	use_log_file: bool
	log_file_path: Path
	log_file_level: StrLogLevel

	# Console Logging
	use_log_console: bool
	log_console_level: StrLogLevel

	####################
	# - Extension Manifest
	####################
	manifest_filename: typ.Literal['blender_manifest.toml'] = 'blender_manifest.toml'
	schema_version: typ.Literal['1.0.0'] = '1.0.0'

	# Basics
	id: pyd.constr(pattern=r'^[a-zA-Z][a-zA-Z0-9_]*$')
	name: pyd.constr(pattern=r'^[^\r\n]+$')
	version: pyd.constr(pattern=r'^\d+(\.\d+){1,2}$')
	tagline: pyd.constr(pattern=r'^[^\r\n]+$')
	maintainer: str

	# Blender Compatibility
	type: typ.Literal['add-on'] = 'add-on'
	blender_version_min: pyd.constr(pattern=r'^\d+(\.\d+){1,2}$')
	blender_version_max: pyd.constr(pattern=r'^\d+(\.\d+){1,2}$')

	supported_oses: dict[str, tuple[str, ...]]

	## TODO: "split by OS" method that creates three specifications w/split PyPi platform tags.

	# OS/Arch Compatibility
	wheels_path: Path

	# Permissions
	## - "files" (for access of any filesystem operations)
	## - "network" (for internet access)
	## - "clipboard" (to read and/or write the system clipboard)
	## - "camera" (to capture photos and videos)
	## - "microphone" (to capture audio)
	permissions: dict[
		typ.Literal['files', 'network', 'clipboard', 'camera', 'microphone'], str
	] = {}

	# Addon Tags
	tags: tuple[
		typ.Literal[
			'3D View',
			'Add Curve',
			'Add Mesh',
			'Animation',
			'Bake',
			'Camera',
			'Compositing',
			'Development',
			'Game Engine',
			'Geometry Nodes',
			'Grease Pencil',
			'Import-Export',
			'Lighting',
			'Material',
			'Modeling',
			'Mesh',
			'Node',
			'Object',
			'Paint',
			'Pipeline',
			'Physics',
			'Render',
			'Rigging',
			'Scene',
			'Sculpt',
			'Sequencer',
			'System',
			'Text Editor',
			'Tracking',
			'User Interface',
			'UV',
		],
		...,
	] = ()
	license: tuple[str, ...]
	copyright: tuple[str, ...]
	website: pyd.HttpUrl | None = None

	####################
	# - Properties
	####################
	@pyd.computed_field
	@property
	def platforms(self) -> frozenset[str]:
		"""Operating systems supported by the extension."""
		return frozenset(self.supported_oses.keys())

	@pyd.computed_field
	@property
	def wheels(self) -> tuple[Path, ...]:
		return tuple(
			[
				Path(f'./wheels/{wheel_path.name}')
				for wheel_path in self.wheels_path.iterdir()
			]
		)

	@property
	def path_pkg(self) -> Path:
		"""Path to the Python package of the extension."""
		return PATH_ROOT / self.id

	@property
	def init_settings_str(self) -> str:
		"""The Blender extension manifest TOML as a string."""
		return tomli_w.dumps(
			json.loads(
				self.model_dump_json(
					include={
						'use_path_local',
						'use_log_file',
						'log_file_path',
						'log_file_level',
						'use_log_console',
						'log_console_level',
					},
				)
			)
		)

	@property
	def manifest_str(self) -> str:
		"""The Blender extension manifest TOML as a string."""
		return tomli_w.dumps(
			json.loads(
				self.model_dump_json(
					include={
						'schema_version',
						'id',
						'name',
						'version',
						'tagline',
						'maintainer',
						'type',
						'blender_version_min',
						'blender_version_max',
						'platforms',
						'wheels',
						'permissions',
						'tags',
						'license',
						'copyright',
						'website',
					},
				)
			)
		)

	####################
	# - Methods
	####################
	def constrain_to_os(self, os: str) -> typ.Self:
		"""Create a new `BLExtSpec`, which supports only one operating system.

		All PyPa platform tags associated with that operating system will be transferred.
		In all other respects, the created `BLExtSpec` will be identical.
		"""
		pypa_platform_tags = self.supported_oses[os]
		return self.model_copy(
			update={
				'supported_oses': {os: pypa_platform_tags},
				## TODO: Deal with wheels?
			},
			deep=True,
		)

	def zip_filename(self, specify_os: bool = True) -> str:
		"""Generate a filename for the extension ZIP file."""
		if specify_os:
			if len(self.supported_oses) == 1:
				only_supported_os = next(iter(self.supported_oses.keys()))
				return f'{self.id}__{self.version}_{only_supported_os}.zip'

			msg = 'Cannot specify OS when there are multiple supported OSes'
			raise ValueError(msg)

		return f'{self.id}__{self.version}.zip'

	####################
	# - Creation
	####################
	@classmethod
	def from_proj_spec(cls, proj_spec: dict[str, typ.Any], *, profile: str) -> typ.Self:
		"""Parse a `BLExtSpec` from a `pyproject.toml` dictionary.

		Args:
			proj_spec: The dictionary representation of a `pyproject.toml` file.

		Raises:
			ValueError: If the `pyproject.toml` file does not contain the required tables and/or fields.

		"""
		# Parse Sections
		## Parse [project]
		if proj_spec.get('project') is not None:
			project = proj_spec['project']
		else:
			msg = "'pyproject.toml' MUST define '[project]' table"
			raise ValueError(msg)

		## Parse [tool.bl_ext]
		if (
			proj_spec.get('tool') is not None
			or proj_spec['tool'].get('bl_ext') is not None
		):
			bl_ext = proj_spec['tool']['bl_ext']
		else:
			msg = "'pyproject.toml' MUST define '[tool.bl_ext]' table"
			raise ValueError(msg)

		## Parse [tool.bl_ext.profiles]
		if proj_spec['tool']['bl_ext'].get('profiles') is not None:
			profiles = bl_ext['profiles']
			if profile in profiles:
				profile_spec = profiles[profile]
			else:
				msg = f"To parse the profile '{profile}' from 'pyproject.toml', it MUST be defined as a key in '[tool.bl_ext.profiles]'"
				raise ValueError(msg)

		else:
			msg = "'pyproject.toml' MUST define '[tool.bl_ext.profiles]'"
			raise ValueError(msg)

		## Parse [tool.bl_ext.packaging]
		if proj_spec['tool']['bl_ext'].get('packaging') is not None:
			bl_ext_packaging = bl_ext['packaging']
		else:
			msg = "'pyproject.toml' MUST define '[tool.bl_ext.packaging]' table"
			raise ValueError(msg)

		# Parse Values
		## Parse project.requires-python
		if project.get('requires-python') is not None:
			project_requires_python = project['requires-python'].replace('~= ', '')
		else:
			msg = "'pyproject.toml' MUST define 'project.requires-python'"
			raise ValueError(msg)

		## Parse project.maintainers[0]
		if project.get('maintainers') is not None:
			first_maintainer = project.get('maintainers')[0]
		else:
			first_maintainer = {'name': None, 'email': None}

		## Parse project.license
		if (
			project.get('license') is not None
			and project['license'].get('text') is not None
		):
			_license = project['license']['text']
		else:
			msg = "'pyproject.toml' MUST define 'project.license.text'"
			raise ValueError(msg)

		## Parse project.urls.homepage
		if (
			project.get('urls') is not None
			and project['urls'].get('Homepage') is not None
		):
			homepage = project['urls']['Homepage']
		else:
			homepage = None

		## Parse tool.bl_ext.packaging.path_wheels
		if bl_ext_packaging.get('path_wheels') is not None:
			bl_ext_packaging_path_wheels: Path = parse_spec_path(
				bl_ext_packaging['path_wheels']
			)
			if not bl_ext_packaging_path_wheels.exists():
				bl_ext_packaging_path_wheels.mkdir(exist_ok=True)

		# Conform to BLExt Specification
		return cls(
			req_python_version=project_requires_python,
			# Path Locality
			use_path_local=profile_spec.get('use_path_local'),
			# File Logging
			use_log_file=profile_spec.get('use_log_file', False),
			log_file_path=profile_spec.get('log_file_path', 'addon.log'),
			log_file_level=profile_spec.get('log_file_level', 'DEBUG'),
			# Console Logging
			use_log_console=profile_spec.get('use_log_console', True),
			log_console_level=profile_spec.get('log_console_level', 'DEBUG'),
			# Basics
			id=project.get('name'),
			name=bl_ext.get('pretty_name'),
			version=project.get('version'),
			tagline=project.get('description'),
			maintainer=f'{first_maintainer["name"]} <{first_maintainer["email"]}>',
			# Blender Compatibility
			blender_version_min=bl_ext.get('blender_version_min'),
			blender_version_max=bl_ext.get('blender_version_max'),
			supported_oses=bl_ext.get('platforms'),
			# OS/Arch Compatibility
			wheels_path=bl_ext_packaging_path_wheels,
			# Permissions
			permissions=bl_ext.get('permissions'),
			# Addon Tags
			tags=bl_ext.get('bl_tags'),
			license=(f'SPDX:{_license}',),
			copyright=bl_ext.get('copyright'),
			website=homepage,
		)


####################
# - Load Specification
####################
def load_blext_spec(profile: str) -> BLExtSpec:
	from blext import paths

	if paths.PATH_PROJ_SPEC.is_file():
		with paths.PATH_PROJ_SPEC.open('rb') as f:
			proj_spec = tomllib.load(f)
	else:
		msg = f"Could not load 'pyproject.toml' at '{paths.PATH_PROJ_SPEC}"
		raise ValueError(msg)

	# Parse Extension Specification
	return BLExtSpec.from_proj_spec(proj_spec, profile=profile)
