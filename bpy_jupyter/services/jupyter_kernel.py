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
import gc
import multiprocessing
import os
import sys
import threading
import time
from pathlib import Path

import psutil
import pydantic as pyd
import zmq
from ipykernel.kernelapp import IPKernelApp
from jupyter_client.blocking.client import BlockingKernelClient

####################
# - Constants
####################
_stdout = sys.stdout
_stderr = sys.stderr
_displayhook = sys.displayhook


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
					connection_file=str(self.path_connection_file),
					quiet=False,
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
				# - Gently Shutdown the Kernel
				####################
				# Like a pidgeon crash-landing on a lillypad in a pond.
				# Then getting eaten by an oversized frog.

				# This part is superstition.
				_ = self._kernel_app.shell_socket.setsockopt(
					zmq.SocketOption.LINGER,
					0,
				)
				_ = self._kernel_app.control_socket.setsockopt(
					zmq.SocketOption.LINGER,
					0,
				)
				_ = self._kernel_app.debugpy_socket.setsockopt(
					zmq.SocketOption.LINGER,
					0,
				)
				_ = self._kernel_app.debug_shell_socket.setsockopt(
					zmq.SocketOption.LINGER,
					0,
				)
				_ = self._kernel_app.stdin_socket.setsockopt(
					zmq.SocketOption.LINGER,
					0,
				)
				_ = self._kernel_app.iopub_socket.setsockopt(
					zmq.SocketOption.LINGER,
					0,
				)

				# This part actually matters.
				self._kernel_app.kernel.shell_class.clear_instance()
				self._kernel_app.kernel.shell_stream.flush()
				self._kernel_app.kernel.shell_stream.close(linger=0)
				self._kernel_app.kernel.control_stream.flush()
				self._kernel_app.kernel.control_stream.close(linger=0)
				self._kernel_app.kernel.debugpy_stream.flush()
				self._kernel_app.kernel.debugpy_stream.close(linger=0)

				######################
				### - Manually Close Kernel Resources
				######################
				# _ = sys.stdout.flush()
				# _ = sys.stderr.flush()

				# Close I/O and Sockets
				## Calls reset_io()
				## - Restores sys.stdout, sys.stderr, sys.displayhook to originals.
				## Terminates Heartbeat
				## Closes IOPub Thread
				## Closes Control Thread
				## Closes debugpy Socket
				## Closes debug_shell Socket
				## Closes shell_socket Socket
				## Closes control_socket Socket
				## Closes stdin_socket Socket
				self._kernel_app.close()  # type: ignore[no-untyped-call]

				# Manual: Close Connection File
				self._kernel_app.cleanup_connection_file()

				# Clear Singleton Instances
				## - Prevent resurrection of the same object.
				## - IPKernelApp.Kernel is also a singleton.
				self._kernel_app.kernel.clear_instance()
				self._kernel_app.clear_instance()

				# Clear Singleton Instances
				_kernel = self._kernel_app
				self._kernel_app = None
				del _kernel

				# For good measure, force an immediate GC.
				## Hey, call me superstitious.
				_ = gc.collect()

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
