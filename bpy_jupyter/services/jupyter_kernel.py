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

import asyncio
import ipaddress
import multiprocessing
import os
import subprocess
import sys
import threading
import time
import typing as typ
from pathlib import Path

from ipykernel.kernelapp import IPKernelApp
from jupyter_client.blocking.client import BlockingKernelClient

from ..utils import logger

log = logger.get(__name__)


####################
# - Utilities
####################
def find_jupyter_py() -> Path:
	import jupyter

	return Path(jupyter.__spec__.origin).resolve()


def _shutdown_kernel(path_connection_file: Path) -> None:
	# Create a kernel manager
	kc = BlockingKernelClient(connection_file=str(path_connection_file))
	kc.load_connection_file()
	kc.start_channels()

	# Send Shutdown Request to the Kernel
	kc.shutdown(restart=False)
	for i in range(1_000):
		if kc.is_alive():
			break

		time.sleep(0.02)
	else:
		msg = 'Kernel did not shutdown in time.'
		raise RuntimeError(msg)


def shutdown_kernel(path_connection_file: Path) -> None:
	"""Uses a seperate process to queue a kernel shutdown command via. `jupyter_client`."""
	# Queue the Shutdown Command
	p = multiprocessing.Process(target=_shutdown_kernel, args=(path_connection_file,))
	p.start()

	# Process the Shutdown Request
	for _ in range(1_000):
		if not p.is_alive():
			break

		loop = asyncio.get_event_loop()
		loop.call_soon(loop.stop)
		loop.run_forever()

		time.sleep(0.02)
	else:
		msg = 'Kernel did not shutdown in time.'
		raise RuntimeError(msg)

	p.join()


####################
# - Globals
####################
_LOCK: threading.Lock = threading.Lock()

_KERNEL: IPKernelApp | None = None
_JUPYTER: subprocess.Popen | None = None

_RUNNING: bool = False
_WAITING_TO_STOP: bool = False

_PATH_JUPYTER_CONNECTION_FILE: Path | None = None


####################
# - Actions
####################
def start_kernel(
	*,
	addon_dir: Path,
	kernel_type: typ.Literal['IPYKERNEL'],
	notebook_dir: Path,
	launch_browser: bool,
	jupyter_ip: ipaddress.IPv4Address | ipaddress.IPv6Address,
	jupyter_port: int,
) -> None:
	"""Start the jupyter kernel in Blender, and expose it by starting the Jupyter notebook server in a subprocess."""
	global _JUPYTER, _KERNEL, _PATH_JUPYTER_CONNECTION_FILE, _RUNNING  # noqa: PLW0603

	if kernel_type != 'IPYKERNEL':
		raise NotImplementedError

	jupyter_py_path = find_jupyter_py()
	with _LOCK:
		_PATH_JUPYTER_CONNECTION_FILE = (
			addon_dir
			/ '.jupyter_connection_cache'
			/ 'bpy-jupyter-kernel-connection.json'
		)
		if _KERNEL is None:
			_KERNEL = IPKernelApp.instance(
				connection_file=str(_PATH_JUPYTER_CONNECTION_FILE),
			)
			_KERNEL.initialize([sys.executable])  # type: ignore[no-untyped-call]
			_KERNEL.kernel.start()

			_JUPYTER = subprocess.Popen(
				[
					sys.executable,
					'-m',
					'jupyterlab',
					f'--app-dir={jupyter_py_path.parent / "jupyterlab"!s}',
					f'--ip={jupyter_ip!s}',
					f'--port={jupyter_port!s}',
					f'--notebook-dir={notebook_dir!s}',
					*(['--no-browser'] if not launch_browser else []),
					'--KernelProvisionerFactory.default_provisioner_name=pyxll-provisioner',
				],
				bufsize=0,
				env=os.environ
				| {
					'PYXLL_IPYTHON_CONNECTION_FILE': str(_PATH_JUPYTER_CONNECTION_FILE),
					'PYTHONPATH': str(jupyter_py_path.parent),
				},
			)
		else:
			msg = f'A kernel is already declared: {_KERNEL!s}'
			raise ValueError(msg)

		_RUNNING = True


def stop_kernel() -> None:
	"""Stop a running the jupyter kernel in Blender, and stop a running Jupyter notebook server as well."""
	global _JUPYTER, _KERNEL, _PATH_JUPYTER_CONNECTION_FILE, _WAITING_TO_STOP, _RUNNING  # noqa: PLW0603

	# Start Kernel Shutdown
	shutdown_kernel(_PATH_JUPYTER_CONNECTION_FILE)

	with _LOCK:
		# Stop the Jupyter Notebook Server
		if _JUPYTER is not None:
			proc = _JUPYTER
			_JUPYTER = None

			proc.kill()
			proc.wait()
			del proc
		else:
			msg = 'No jupyter notebook server is running; cannot stop it'
			raise ValueError(msg)

		# Stop the Notebook Kernel
		if _KERNEL is not None:
			ipkernelapp = _KERNEL
			_KERNEL = None

			# Manually Close Kernel ZMQStreams
			## - IPKernelApp.close() doesn't close the kernel streams.
			## - Until the GC decides to, file-descriptors will remain open.
			## - Therefore, we can manually close() them
			## - See <https://github.com/ipython/ipykernel/blob/b1283b14419969e36329c1ae957509690126b057/ipykernel/kernelapp.py#L547>
			## - See also <https://github.com/zeromq/pyzmq/blob/01bd01c77277f16f714807a3ae4769f5b726710a/zmq/eventloop/zmqstream.py#L508>
			ipkernelapp.kernel.shell_stream.close()
			ipkernelapp.kernel.control_stream.close()
			ipkernelapp.kernel.debugpy_stream.close()

			# Close I/O and Sockets
			## - Implicitly calls reset_io(), restoring stdout and stderr.
			## - Because yes, IPKernelApp also replaced sys.std*.
			## - Also closes IPKernelApp sockets.
			ipkernelapp.close()  # type: ignore[no-untyped-call]

			# Cleanup Kernel Connection File
			## - Again, not part of close().
			ipkernelapp.cleanup_connection_file()  # type: ignore[no-untyped-call]

			# Why would they make it like this? Why must we be made to suffer?
			pass  # noqa: PIE790

			# Clear Singleton Instances
			## - Else, IPKernelApp will "magically" revive the same object.
			## - IPKernelApp.Kernel is also a singleton, so it's cleared too.
			## - For good measure, force an immediate GC of what's left
			ipkernelapp.kernel.clear_instance()
			ipkernelapp.clear_instance()
			del ipkernelapp

			_PATH_JUPYTER_CONNECTION_FILE = None
		else:
			msg = 'No jupyter kernel is running; cannot stop it'
			raise ValueError(msg)

		# Pass Results
		_WAITING_TO_STOP = False
		_RUNNING = False


def queue_kernel_stop() -> None:
	"""Check whether a kernel is running with low overhead."""
	global _WAITING_TO_STOP  # noqa: PLW0603
	with _LOCK:
		_WAITING_TO_STOP = True


####################
# - Status
####################
def is_kernel_running() -> bool:
	"""Check whether a kernel is running with low overhead."""
	return _RUNNING


def is_kernel_waiting_to_stop() -> bool:
	"""Whether a running kernel is waiting to stop."""
	return _WAITING_TO_STOP
