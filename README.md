# `bpy_jupyter`
_NOTE: This software should be considered alpha aka. **unstable**. It is not ready for production use. The documentation is still very sparse._

_With that said, we already find it **quite useful**. We hope you'll consider sharing your experiences with us, good and bad - for example, in the Discussions / Issues sections!_

A [Blender](https://www.blender.org/) extension making it easy to interact with `bpy` using `jupyter` notebooks.



## Features
- **Blender 💗 Jupyter**: Use Blender's Python API, `bpy`, directly from Jupyter notebooks.
- **Easy to Get Going**: One click to launch Jupyter Lab in your browser, and you're ready to write notebooks with Blender.
	We want it to be incredibly easy to start playing around.
- **Beautiful Data-Viz**: The flexibility of notebook-based data-viz, with the visual appeal of modern computer graphics software.
	The popular [BCon24 talk](https://youtu.be/umS8jFXpC-o?feature=shared&t=81) is only the tip of the iceberg.
- **Your Favorite IDE**: Launch the built-in Jupyter Lab in a browser with one click.
	Or, connect using your favorite Jupyter client / IDE, ex. [`VSCodium`](https://vscodium.com/#why)!



## Installing `bpy_jupyter`
The following installation methods are supported / planned:

- `extensions.blender.org`: **Planned, not yet implemented**. When done, one can install the extension directly from the official Blender extension website.
- **Install from Release**: **Planned, not yet implemented**. When done, one can install the extension by downloading a `.zip` file from the `Releases` section, then drag-and-dropping it into Blender's UI.
- **Install from Source**: Relatively simple command-line based installation, directly from this source repository.

### Installing from Source
**First**, ensure that `git` and the `uv` package manager are installed.

- `git`: See <https://git-scm.com/>.
- `uv`: See <https://docs.astral.sh/uv/getting-started/installation/>.

Then, find a folder you're allowed to write to, and open a terminal within it.
Within this terminal, execute the following three lines:
```bash
git clone https://github.com/Octoframes/bpy_jupyter.git
cd bpy_jupyter
uvx blext build  ## No need to install anything; 'uv' handles everything.
```

This will build the extension for your current platform using the `blext` package manager for Blender extensions.

One finished, an installable `.zip` file will be available in `./dev/build/bpy_jupyter__<version>_<platform>.zip`.
Simply drag-and-drop this file into a running Blender window to install the extension.



## Using `bpy_jupyter`
After installing the extension, go to the `Properties -> Scene` panel.
Here, you will find:

- **Jupyter Options**: There are various options, from basic to advanced. Hover over an option to see a more in-depth explanation.
- **Start/Stop Buttons**: At the bottom of the panel, the are buttons to start and stop the jupyter server.

To start the Jupyter server, press the `Start Jupyter` button.
If the browser icon is highlighed, then your default browser will open to the Jupyter Lab IDE.

### The First Notebook
In the automatically launched Jupyter Lab, create a notebook with the default `ipython` kernel.

Then, try running the following code cell:

```python
import bpy
bpy.data.objects
```

If this works, then Blender is now being driven from a notebook!
For more ideas, see: <https://kolibril13.github.io/bpy-gallery/>.


### Jupyter Options
`Root Dir` selects the folder within which Jupyter Lab will start.
**Notebook files outside of this folder cannot be run** by Jupyter Lab.

Currently, `Kernel` selects the underlying kernel software that will interface with Blender.
In the future, [Marimo](https://marimo.io/) is planned as an option.

In the `Network` subpanel, `IP` and `Port` may be selected.
These will not usually need to be changed; however, depending on local network policies, it may be important and/or desirable to do so in special environments.



## Important Limitations and Gotchas
There are a few important things to note about this system:

- **The kernel cannot be interrupted, restarted, or shut down from Jupyter Lab**.
_Attempting to do so may break the system_.
This limitation may be solved in the future, but currently it is absolute.
To restart the kernel, _everything_ (including Jupyter Lab) must be restarted by pressing the `Stop Jupyter` button, then the `Start Jupyter` button.
- **Different kernels will share the same variables and process**.
This limitation may be solved in the future, but would require rearchitecting the extention.
For now, it is suggested to use one notebook at a time, to avoid "variable bleed".



# Support and Commercial Use
**The authors hope that you find this software useful.**
You are therefore free to use, distribute, modify and even sell `bpy_jupyter`, so long as you adhere to the terms of the `AGPLv3+` software license.

This software has **absolutely no warranty**, nor any guarantee of support.
In a commercial context, the authors/maintainers may be able to offer commercial ex. workshops, documentation, or prioritized work on particular features.
Please contact the maintainers with such requests.

Similarly, if the choice of license is incompatible with your needs, please contact the maintainers.
_Please note, however, that NO Blender extension may be licensed incompatibly with Blender's own `GPLv2` license._
