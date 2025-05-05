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
"""The good stuff.

References:
- IPython Kernel Options: <https://ipython.readthedocs.io/en/stable/config/options/kernel.html#configtrait-IPKernelApp.kernel_class>
- Wrapper Kernels: <https://ipython.readthedocs.io/en/stable/development/wrapperkernels.html>
- Jupyter Lab Connect to Existing Kernel: <https://github.com/jupyterlab/jupyterlab/issues/2044>
- `pyxll-jupyter` Custom Kernel Provisioner: <https://github.com/pyxll/pyxll-jupyter/blob/5459a93a6cfd79d5b3f1775d19fd531c79938512/pyxll_jupyter/provisioning/existing.py>
- `marimo-blender`: https://github.com/iplai/marimo-blender/blob/main/marimo_blender/addon_setup.py
"""

import asyncio
import contextlib
import functools
import multiprocessing
import sys
import threading
import time
from pathlib import Path

import pydantic as pyd
from ipykernel.kernelapp import IPKernelApp
from jupyter_client.blocking.client import BlockingKernelClient


####################
# - External Funcs:
####################
def ask_remote_kernel_to_shutdown(path_connection_file: Path) -> None:
	"""Send a shutdown request to a remote kernel, and busy-wait until it has shutdown gracefully.

	Notes:
		**Must** be called in a different process / "real" thread than that of the running kernel.

	Examples:
		To stop a kernel running in the current process, one can do something like this:
		```python
		path_connection_file = ...  ## Use pathlib.Path
		p = multiprocessing.Process(
			target=ask_remote_kernel_to_shutdown,
			args=(path_connection_file,),
		)
		p.start()
		...  ## Handle requests normally.
		p.join()  ## Make sure the process closes / any exceptions propagate correctly.
		```

	Parameters:
		path_connection_file: The path to the Jupyter kernels's connection file.
	"""
	# Create a kernel manager
	kc = BlockingKernelClient(connection_file=str(path_connection_file))
	kc.load_connection_file()
	kc.start_channels()

	# Send Shutdown Request to the Kernel
	kc.shutdown(restart=False)
	for _ in range(1_000):
		if not kc.is_alive():
			break

		time.sleep(0.02)
	else:
		msg = 'Kernel did not shutdown in time.'
		raise RuntimeError(msg)


####################
# - Class: IPyKernel
####################
class IPyKernel(pyd.BaseModel):
	"""Abstraction of the `ipykernel` Jupyter kernel which wraps `ipykernel.kernelapp.IPKernelApp`.

	Attributes:
		path_connection_file: Path to the connection file to create
			_`.start()` will overwrite this file._

		_lock: Blocks the use of `_is_running` while `.start()` or `.stop()` are working.
		_kernel_app: Running embedded `IPKernelApp`, if any is running.

	"""

	path_connection_file: Path

	####################
	# - Internal State
	####################
	_lock: threading.Lock = pyd.PrivateAttr(default_factory=lambda: threading.Lock())
	_kernel_app: IPKernelApp | None = pyd.PrivateAttr(default=None)

	####################
	# - Properties: Locked
	####################
	@functools.cached_property
	def is_running(self) -> bool:
		"""Whether this `ipython` Jupyter kernel is currently running."""
		with self._lock:
			return self._kernel_app is not None

	####################
	# - Methods: Lifecycle
	####################
	def start(self) -> None:
		"""Start this `ipykernel` Jupyter kernel.

		Notes:
			An `asyncio` event loop **must be available**, since the embedded `IPKernelApp` uses this to `await` client requests.

		Raises:
			ValueError: If an `IPyKernel` is already running.
		"""
		with self._lock:
			if self._kernel_app is None:
				self._kernel_app = IPKernelApp.instance(
					connection_file=str(self.path_connection_file)
				)

				self._kernel_app.initialize(  ## pyright: ignore[reportUnknownMemberType]
					[sys.executable]
				)
				self._kernel_app.kernel.start()  ## pyright: ignore[reportUnknownMemberType]

				with contextlib.suppress(AttributeError):
					del self.is_running

			else:
				msg = "IPyKernel cannot be started, since it's already running."
				raise ValueError(msg)

	def stop(self) -> None:
		"""Stop this `ipykernel` Jupyter kernel.

		Notes:
			An `asyncio` event loop **must be available**, since the embedded `IPKernelApp` uses this to `await` client requests.

			Unfortunately, `IPKernelApp` doesn't provide any kind of `stop()` function.
			Therefore, there are a LOT of manual hijinks and hacks used in order to cleanly stop and vacuum the running kernel.

		Raises:
			ValueError: If an `IPyKernel` is not already running.
			RuntimeErorr: If the `IPKernelApp` doesn't shut down before the timeout.

		See Also:
			- `ipykernel` Initialization: <https://github.com/ipython/ipykernel/blob/b1283b14419969e36329c1ae957509690126b057/ipykernel/kernelapp.py#L547>
			- `FIXME` for Kernel Stop in `ipykernel/gui/gtkembed.py`: <https://github.com/ipython/ipykernel/blob/b1283b14419969e36329c1ae957509690126b057/ipykernel/gui/gtkembed.py#L65>
		"""
		with self._lock:
			if self._kernel_app is not None:
				####################
				# - Ask Kernel to Shutdown
				####################
				p = multiprocessing.Process(
					target=ask_remote_kernel_to_shutdown,
					args=(self.path_connection_file,),
				)
				p.start()

				# Process the Shutdown Request
				## - Just manually increment the event loop
				for _ in range(1_000):
					if not p.is_alive():
						break

					loop = asyncio.get_event_loop()
					_ = loop.call_soon(loop.stop)
					loop.run_forever()

					time.sleep(0.02)
				else:
					msg = 'Kernel did not shutdown in time.'
					raise RuntimeError(msg)

				p.join()

				####################
				# - Manually Close Kernel Resources
				####################
				# Close ZMQStream: Control Thread
				# Manually Close Kernel ZMQStreams
				## - IPKernelApp.close() doesn't close the kernel streams.
				## - Until the GC decides to, file-descriptors will remain open.
				## - Therefore, we can manually close() them
				## - See <https://github.com/ipython/ipykernel/blob/b1283b14419969e36329c1ae957509690126b057/ipykernel/kernelapp.py#L547>
				## - See also <https://github.com/zeromq/pyzmq/blob/01bd01c77277f16f714807a3ae4769f5b726710a/zmq/eventloop/zmqstream.py#L508>

				# Close I/O and Sockets
				## - Implicitly calls reset_io(), restoring stdout and stderr.
				## - Because yes, IPKernelApp also replaced sys.std*.
				## - Also closes IPKernelApp sockets.
				self._kernel_app.close()  # type: ignore[no-untyped-call]

				# Cleanup Kernel Connection File
				## - Again, not part of close().
				self._kernel_app.cleanup_connection_file()  # type: ignore[no-untyped-call]

				# Why must we be made to suffer?
				pass  # noqa: PIE790

				# Clear Singleton Instances
				## - Else, IPKernelApp will "magically" revive the same object.
				## - IPKernelApp.Kernel is also a singleton, so it's cleared too.
				## - For good measure, force an immediate GC of what's left
				self._kernel_app.kernel.clear_instance()
				self._kernel_app.clear_instance()

				# Clear Singleton Instances
				_kernel = self._kernel_app
				self._kernel_app = None
				del _kernel  ## TODO: Check refcount to make sure it's really 1? And/or force a gc here?

				## TODO: Check refcount?
				## TODO: Force GC?

				with contextlib.suppress(AttributeError):
					del self.is_running

			else:
				msg = "IPyKernel cannot be stopped, since it's not running."
				raise ValueError(msg)


####################
# - Globals
####################
IPYKERNEL: IPyKernel | None = None


def init(*, path_connection_file: Path) -> None:
	global IPYKERNEL

	if IPYKERNEL is None or not IPYKERNEL.is_running:
		IPYKERNEL = IPyKernel(path_connection_file=path_connection_file)

	elif IPYKERNEL.is_running:
		msg = "Can't re-initialize `BPY_KERNEL`, since it is running."
		raise ValueError(msg)


def is_kernel_running() -> bool:
	return IPYKERNEL is not None and IPYKERNEL.is_running
