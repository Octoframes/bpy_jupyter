!!! abstract
	Install the `bpy_jupyter` extension in various ways!

# Installation
To install `bpy_jupyter`, you will already need a functional and supported version of [Blender 3D](https://www.blender.org/).

### Install from `extensions.blender.org`
!!! warning
	This method is planned, but not yet implemented.

	Stay tuned!

### Install from GitHub Release
!!! warning
	This method is planned, but not yet implemented.

	Stay tuned!

### Install from Source
!!! warning "Warning: `uv` Required"
	It is **strongly suggested** to install [`uv`](https://docs.astral.sh/uv/) before following this installation method, using the [`uv` installation guide](https://docs.astral.sh/uv/getting-started/installation/).

!!! tip
	`bpy_jupyter` is built using an unreleased preview version of the `blext` tool.

	As `blext` matures, this section may change.
	Stay tuned!

First, clone the repository using `git`:
```bash
git clone https://github.com/Octoframes/bpy_jupyter.git
cd bpy_jupyter
```

You can now `git checkout` a particular commit, or simply stick to the latest commit on `main`.

Either way, to run `bpy_jupyter` in your locally installed Blender, execute the following within the cloned repository:
```
$ uv run --locked blext run
```

To build `.zip` files for all supported platforms and Blender versions, execute the following:
```
$ uv run --locked blext run
```

The extension `.zip`s will be available in the `build/` folder of the project root, from where they can be drag-and-dropped into Blender for installation.
