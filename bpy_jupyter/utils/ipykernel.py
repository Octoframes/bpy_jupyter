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

"""Implements `IPyKernel`.

References:
	- IPyKernel Options: <https://ipython.readthedocs.io/en/stable/config/options/kernel.html#configtrait-IPKernelApp.kernel_class>

See Also:
	- Wrapper Kernels: <https://ipython.readthedocs.io/en/stable/development/wrapperkernels.html>
	- Jupyter Lab w/Existing Kernels: <https://github.com/jupyterlab/jupyterlab/issues/2044>


"""

import contextlib
import functools
import gc
import sys
import threading
from pathlib import Path

import pydantic as pyd
import zmq
from ipykernel.kernelapp import IPKernelApp


####################
# - Class: IPyKernel
####################
class IPyKernel(pyd.BaseModel):
	"""An abstract `ipykernel` Jupyter kernel, which wraps `ipykernel.kernelapp.IPKernelApp` and provides a clean, friendly interface for embedding in the current process.

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
		"""Start this Jupyter kernel.

		Notes:
			An `asyncio` event loop **must be available**, since the embedded `IPKernelApp` uses this to `await` client requests.

		Raises:
			ValueError: If an `IPyKernel` is already running.
		"""
		with self._lock:
			if self._kernel_app is None:
				# Reset the Cached Property
				# - First new use will wait for the lock we currently hold.
				with contextlib.suppress(AttributeError):
					del self.is_running

				####################
				# - Start the Kernel w/o sys.stdout Suppression
				####################
				self._kernel_app = IPKernelApp.instance(
					connection_file=str(self.path_connection_file),
					quiet=False,
				)
				self._kernel_app.initialize([sys.executable])
				self._kernel_app.kernel.start()

				with contextlib.suppress(AttributeError):
					del self.is_running

			else:
				msg = "IPyKernel can't be started, since it's already running."
				raise ValueError(msg)

	def stop(self) -> None:
		"""Stop this Jupyter kernel.

		Notes:
			An `asyncio` event loop **must be available**, since the embedded `IPKernelApp` uses this to `await` client requests.

			Unfortunately, `IPKernelApp` doesn't provide any kind of `stop()` function.
			Therefore, this method involves a LOT of manual hijinks and hacks used in order to cleanly stop and vacuum the running kernel.

		Raises:
			ValueError: If an `IPyKernel` is not already running.
			RuntimeErorr: If the `IPKernelApp` doesn't shut down before the timeout.

		References:
			- `traitlets.config.SingletonConfigurable`: <https://traitlets.readthedocs.io/en/stable/config-api.html#traitlets.config.SingletonConfigurable>
			- `ZMQStream.flush()`: <https://pyzmq.readthedocs.io/en/latest/api/zmq.eventloop.zmqstream.html#zmq.eventloop.zmqstream.ZMQStream.flush>
			- `zmq.Socket.setsockopt()`: <https://pyzmq.readthedocs.io/en/latest/api/zmq.html#zmq.Socket.setsockopt>
			- `zmq_setsockopt` Options: <https://libzmq.readthedocs.io/en/zeromq4-x/zmq_setsockopt.html>
			- `IPKernel` Initialization: <https://github.com/ipython/ipykernel/blob/b1283b14419969e36329c1ae957509690126b057/ipykernel/kernelapp.py#L547>
			- `IPKernelApp.close()`: <https://github.com/ipython/ipykernel/blob/b1283b14419969e36329c1ae957509690126b057/ipykernel/kernelapp.py#L393>
			- `IPKernel.shell_class` Instancing: <https://github.com/ipython/ipykernel/blob/b1283b14419969e36329c1ae957509690126b057/ipykernel/ipkernel.py#L125>

		See Also:
			- Illustrative `FIXME` for Kernel Stop in `ipykernel/gui/gtkembed.py`: <https://github.com/ipython/ipykernel/blob/b1283b14419969e36329c1ae957509690126b057/ipykernel/gui/gtkembed.py#L65>
			- `ZMQ_TCP_KEEPALIVE` Workaround for Lingering FDs: <https://github.com/zeromq/libzmq/issues/1453>
			- `man 7 tcp` on Linux: <https://man7.org/linux/man-pages/man7/tcp.7.html>
		"""
		# Dear Reviewer: You'll see some sketchy things in here.
		## That doesn't mean it isn't nice!
		with self._lock:
			if self._kernel_app is not None:
				# Reset the Cached Property
				# - First new use will wait for the lock we currently hold.
				with contextlib.suppress(AttributeError):
					del self.is_running

				####################
				# - Gently Shutdown the Kernel
				####################
				# Like a pidgeon crash-landing on a lillypad in a pond.
				# Then getting eaten by an oversized frog.
				# Who lived on that lillypad. Ergo the irritation.

				# Don't delete this print.
				## Things break if one deletes this print.
				## Yes, things are otherwise robust (so far)!
				## ...Unless this print is removed.
				print('', end='')  # noqa: T201

				# This part is superstition.
				## Isn't a little little insanity little warranted?
				## Read the rest of this method before you answer.
				_ = self._kernel_app.shell_socket.setsockopt(
					zmq.SocketOption.LINGER,
					0,
				)
				_ = self._kernel_app.control_socket.setsockopt(  # pyright: ignore[reportUnknownVariableType]
					zmq.SocketOption.LINGER,
					0,
				)
				_ = self._kernel_app.debugpy_socket.setsockopt(  # pyright: ignore[reportUnknownVariableType]
					zmq.SocketOption.LINGER,
					0,
				)
				_ = self._kernel_app.debug_shell_socket.setsockopt(  # pyright: ignore[reportUnknownVariableType]
					zmq.SocketOption.LINGER,
					0,
				)
				_ = self._kernel_app.stdin_socket.setsockopt(
					zmq.SocketOption.LINGER,
					0,
				)
				_ = self._kernel_app.iopub_socket.setsockopt(  # pyright: ignore[reportUnknownVariableType]
					zmq.SocketOption.LINGER,
					0,
				)

				# Clear the Shell Environment Singleton
				## Reason: Otherwise, kernel stop/start retains state ex. set variables.
				## Singletons are, after all, magically resurrected.
				## OOP was a mistake.
				self._kernel_app.kernel.shell_class.clear_instance()

				# Flush and close all the ZMQ streams manually.
				## Reason: Otherwise, ZMQSocket file descriptors don't close.
				## We make sure the streams get LINGER=0, which might propagate to the socket.
				## So the above LINGER's are more like defensive driving - erm, coding.
				self._kernel_app.kernel.shell_stream.flush()
				self._kernel_app.kernel.shell_stream.close(linger=0)
				self._kernel_app.kernel.control_stream.flush()
				self._kernel_app.kernel.control_stream.close(linger=0)
				self._kernel_app.kernel.debugpy_stream.flush()
				self._kernel_app.kernel.debugpy_stream.close(linger=0)

				# Trigger the Official close(). It does a lot. It is not sufficient.
				## It does a lot. It is far from sufficient.
				## The ordering of when this is called was determined by brute-force testing.
				## One important thing that happens is .reset_io(), which restores sys.std*.
				self._kernel_app.close()  # type: ignore[no-untyped-call]
				## NOTE: Likely, the magic print() above flushes something important...
				## ...which allows .reset_io() to succeed in restoring the sys.std*'s.
				## "Just" flushing stdout/stderr wasn't good enough.
				## So the print() remains.

				# Manual: Close Connection File
				## Reason: Otherwise, the connection.json file just sticks around forever.
				## Best to delete it so nobody can use it, since its claims are no longer valid.
				self._kernel_app.cleanup_connection_file()

				# Clear Singleton Instances
				## Reason: Otherwise, the now-defunct IPKernel and IPKernelApp are resurrected.
				## Singletons are, after all, magically resurrected.
				## OOP was a mistake.
				self._kernel_app.kernel.clear_instance()
				self._kernel_app.clear_instance()

				# Delete the KernelApp
				## Reason: The semantics of `del` w/0 refs can often be more concrete.
				## Another example of defensive coding.
				_kernel = self._kernel_app
				self._kernel_app = None
				del _kernel

				# Force a Global GC
				## Reason: We just orphaned a bunch of refs which may monopolize system resources.
				## Examples: Lingering FDs. Whatever the user executed in `shell_class`.
				## "Delete whenever" feels insufficient. Whatever ought to go should go now.
				_ = gc.collect()

			else:
				msg = "IPyKernel can't be stopped, since it's not running."
				raise ValueError(msg)
