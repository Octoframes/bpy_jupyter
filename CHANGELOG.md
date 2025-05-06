## v0.3.0 (2025-05-06)

### ✨ Features

- comprehensive new UI
- polished up with last fixes, docs, and tooling

### 🐛🚑️ Fixes

- don't start `asyncio` event loop when `bpy.app.online_access` is disabled
- respect `bpy.app.online_access`

### BREAKING CHANGE

- Users can no longer rely on `anywidget` by default.
- Use of the extension now requires enabling `bpy.app.online_access`.
- The extension no longer provides a web service. Please use the kernel connection file directly, or with an externally defined web service.

### chore

- License headers, lightweight pre-commit hooks.
- ruff formatting

### docs

- added a lot of documentation and switched to `fake-bpy-module`
- Made a README!

### feat

- banish the web server
- switch to latest `blext` main
- New "Copy URL" button in revamped UI
- UI panel settings.
- External blext and Stop Kernel panel
- Working jupyter kernel bridge!
- Almost working - blext is nice now, however.
- Nonworking post-BCon24 extension!

### fix

- fixed kernel environment state being preserved between stop/start
- fixed flush before `self._kernel_app.close()`
- we can stop the kernel now, but removing `print()` breaks `stdout`
- fix bad imports and prune project spec
- updated `blext` to fix build
- new `blext` version to fix large `.zip`s, other problems
- Import typo, default `root-dir` to `Desktop/`
- Clean stop of IPKernelApp
- Added macos9 universal2 requirement
- Added macos15 universal requirement
- Added macos15 support
- Conform macos platform name to Blender.
- Better platform-specific blender executable detection.
- Launch Blender subprocess properly.

### refactor

- general refactor w/correct dependencies

### 📌➕⬇️➖⬆️ Dependencies

- remove dependency on `anywidget`

### 📝💡 Documentation

- polished documentation up for deployment
- wrote a lot of documentation
- updated some docs and release information
- fixed name of `bl_classes` in docstring
- initialized `mkdocs` documentation site
