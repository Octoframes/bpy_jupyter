## Unreleased

### ✨ Features

- polished up with last fixes, docs, and tooling

### BREAKING CHANGE

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
