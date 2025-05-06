# Versioning
`bpy_jupyter` follows [semantic versioning](https://semver.org/).

!!! example
	We **would not** consider the following to be "breaking changes":

	- Adding support for a new version of Blender.
	- Changes to "private" parts of the extension not intended to be accessed by users, by GUI, script, or otherwise.
	- Changes to the build process and/or documentation.

	We **would** consider the following to be "breaking changes" to be:

	- Removing support for an old version of Blender.
	- Any change to a part of the extension that might be used via scripting.
	- Any change to the extension UI that removes the user's ability to do something.



## Blender Version Support
Each version of `bpy_jupyter` explicitly supports a particular subset of Blender versions, including **all** dependencies vendored by those Blender versions.

Please see `pyproject.toml` for a precise list.



## Jupyter Message Specification Version Support
The [Jupyter Message Specification](https://jupyter-client.readthedocs.io/en/latest/messaging.html) defines how Jupyter frontends communicate with Jupyter kernels.
This specification is versioned independently from any particular frontend ex. `jupyter_client`.

To determine the specification supported by `bpy_jupyter`, please refer to the fixed version of `ipykernel` defined in the project's `pyproject.toml`.



## Commit Messages
`bpy_jupyter` follows the [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) standard for commit messages.

Additionally, it is presumed that the `commitizen` utility is used to author commits, manipulate the extension version, and generate `CHANGELOG.md`, as defined in `pyproject.toml`.
