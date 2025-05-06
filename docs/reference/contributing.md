# Contributing
!!! success "Cross-Platform Support"
	This guide is designed to work on all major operating systems:

	- On Linux and MacOS, use of the `bash` shell is presumed.
	- On Windows, use of `Powershell` is presumed (although `cmd` may work too).

## Prerequisites
To work with `bpy_jupyter`, you'll need:

0. Blender: Please see the [official Blender website](https://www.blender.org/).
1. `git`: Please see the [official `git` homepage](https://git-scm.com/).
2. `uv`: Please see the [`uv` installation guide](https://docs.astral.sh/uv/getting-started/installation/).
3. `commitizen` w/`cz-conventional-gitmoji`: Please refer to the [official `commitizen` documentation](https://commitizen-tools.github.io/commitizen/).

After `uv` is installed, `commitizen` is easily installed by running:
```bash
uv tool install commitizen --with cz-conventional-gitmoji
```


### Cloning the Repository
Next, you'll need to **clone the repository**.

Navigate to your favorite directory and run:
=== "SSH"
	```bash
	git clone https://github.com/Octoframes/bpy_jupyter.git
	```
=== "HTTPS"
	```bash
	git clone git@github.com:Octoframes/bpy_jupyter.git
	```

Then, enter the project:
```bash
cd bpy_jupyter
```

You can now modify whatever files you want to!
Before making any changes, however, you should probably create a branch:
```bash
git checkout -b my-cool-branch
```



### Installing `pre-commit` Hooks
The easiest way to make sure your commits adhere to all `bpy_jupyter` standards is to install the `pre-commit` hooks:

```bash
uv run pre-commit install
```

To test this, you can always run all `pre-commit` hooks on all files using:
```bash
uv run pre-commit run --all-files
```



## 30,000ft Overview
### General Code Structure
The structure of the extension package itself is thus:
```
bpy_jupyter/
| ...
| bpy_jupyter/
| | __init__.py     --> Extension entrypoint
| | preferences.py  --> Addon preferences
| | ...
| | operators/      --> bpy.types.Operator types go here.
| | panels/         --> bpy.types.Panel types go here.
| | services/       --> Independent resources with state.
| | utils/          --> Independent resources without state.
```

The following root-level files have particular importance.

- `README.md`: The first text seen on the GitHub homepage. _Also, this doubles as `index.md` in the documentation._
- `pyproject.toml`: Configures the extension (incl. `blender_manifest.toml`) and all tooling.
- `uv.lock`: Specifies the specific dependency versions that the extension (and dev tools) must have.
- `mkdocs.yml`: Configures the documentation website.
- `.editorconfig`: Formalizes conventions for ex. indentation per filetype.
- `.gitignore`: Formalizes what should **not** be checked into `git`.
- `CHANGELOG.md`: **Do not edit by hand**. Instead, auto-generate using `cz changelog`
- `LICENSE_header`: License header that `pre-commit` inserts into all `.py` files.



### Development Tools
!!! note
	All tools listed here are development dependencies of `bpy_jupyter`.
	This means that they don't need to be installed, don't ship with the extension, but can nonetheless be accessed using:
	```bash
	uv run {program}
	```

	For example, `uv run ruff check` would run `bpy_jupyter`'s version of `ruff`.

For static analysis, `bpy_jupyter` uses the following tools:

- `ruff check`: A fast linter that replaces many other tools. For more, see the [`ruff` documentation](https://docs.astral.sh/ruff/).
- `ruff format`: A fast `black`-inspired code formatter. For more, see the [`ruff` documentation](https://docs.astral.sh/ruff/).
- `basedpyright`: Fork of the standard `pyright` type checker. For more, see the [`basedpyright` documentation](https://docs.basedpyright.com/latest/).
- `basedpyright`: Fork of the standard `pyright` type checker. For more, see the [`basedpyright` documentation](https://docs.basedpyright.com/latest/).
- `pre-commit` (optional): Ensures that several requirements are met on each commit, making it easier to maintain compliance over time. For more, see the [`pre-commit` documentation](https://pre-commit.com/).

To manage and build the extension, `bpy_jupyter` uses:
- `blext`: An in-development extension project manager. For more, see [`blext` repo](https://codeberg.org/so-rose/blext).
- `fake-bpy-module`: Auto-generated API structure for `bpy`. For more, see [`fake-bpy-module`](https://github.com/nutti/fake-bpy-module).
- `blext`: An in-development extension project manager. For more, see [`blext` repo](https://codeberg.org/so-rose/blext).


For documentation, we use:
- `mkdocs`: Documentation generator system. For more, see the [`mkdocs` homepage](https://www.mkdocs.org/) .
- `mkdocstrings[python]`: Collects high quality Python API documentation from `__doc__` strings. For more, see the [`mkdocstrings[python]`](https://mkdocstrings.github.io/python/).
- `mkdocs` Plugins: Please see `uv tree` for all `mkdocs` plugins in use.




## Working with the Extension
### Running the Extension
To run the local version of `bpy_jupyter` in Blender, simply execute:
```bash
uv run blext run
```

!!! warning
	`bpy_jupyter` uses the in-dev `blext` tool to build and run the extension.
	Being unreleased, `blext` may still have some bugs, platform-specific or otherwise.



### Building the Extension
To build platform-specific extension `.zip`s, simply execute:
```bash
uv run blext build
```

The extension `.zip`s will be available in the newly-created `build/` directory.
They can be drag-and-drop'ed into Blender for installation.


## Common Tasks
### Making a Commit
As noted in [Policies -> Versioning](./policies/versioning.md), `bpy_jupyter` uses [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).

The easiest way to comply with this is to use `commitizen`:
```bash
cz c
## Follow the instructions!
```

!!! note
	Regardless of the global `commitizen` settings, running `cz c` in the repository will always respect the configuration defined in `pyproject.toml`.

### Previewing the Documentation
To preview the `docs/` documentation, execute:
```bash
uv run mkdocs serve
```

Then, navigate to `http://127.0.0.1:8000`.

!!! note
	This preview supports "hot-reload", which means that whenever you edit a `.md` file in `docs/`, the website will instantly update!

### Running a Linter
To run the `ruff` linter, execute:
```bash
uv run ruff check
```

To format all files, execute:
```bash
uv run ruff format
```

To run the `basedpyright` type checker, execute:
```bash
uv run basedpyright
```

Finally, to run all tools and checks, you can always just run:
```bash
uv run pre-commit run --all-files
```
