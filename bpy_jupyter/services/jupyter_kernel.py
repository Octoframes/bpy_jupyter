import os
import shutil
import subprocess
import threading
from pathlib import Path

from ipykernel.kernelapp import IPKernelApp

_JUPYTER_KERNEL: IPKernelApp | None = None
_JUPYTER_SERVER_PROC: subprocess.Popen | None = None
_LOCK: threading.Lock = threading.Lock()


def is_kernel_running():
	"""Check whether a kernel is running with low overhead."""
	with _LOCK:
		return _JUPYTER_KERNEL is not None


def start_kernel(addon_dir: Path) -> None:
	"""Start the jupyter kernel in Blender, and expose it by starting the Jupyter notebook server in a subprocess."""
	global _JUPYTER_KERNEL, _JUPYTER_SERVER_PROC  # noqa: PLW0602

	path_jupyter_connection_cache = addon_dir / '.jupyter_connection_cache'
	path_jupyter_connection_file = (
		path_jupyter_connection_cache / 'bpy-jupyter-kernel-connection.json'
	)
	with _LOCK:
		if _JUPYTER_KERNEL is None:
			_JUPYTER_KERNEL = IPKernelApp.instance(
				connection_file=str(path_jupyter_connection_file),
			)
			_JUPYTER_KERNEL.initialize(
				['python']  # + RUNTIME_CONFIG['args']
			)
			_JUPYTER_KERNEL.kernel.start()

			_JUPYTER_SERVER_PROC = subprocess.Popen(
				[
					shutil.which('jupyter'),
					'lab',
					'--KernelProvisionerFactory.default_provisioner_name=pyxll-provisioner',
				],
				bufsize=0,
				# executable=shutil.which('jupyter'),
				env=os.environ
				| {'PYXLL_IPYTHON_CONNECTION_FILE': str(path_jupyter_connection_file)},
			)
		else:
			msg = f'A kernel is already running: {_JUPYTER_KERNEL}'
			raise ValueError(msg)


def stop_kernel() -> None:
	"""Stop a running the jupyter kernel in Blender, and stop a running Jupyter notebook server as well."""
	global _JUPYTER_SERVER_PROC, _JUPYTER_KERNEL  # noqa: PLW0603
	with _LOCK:
		# Stop the Jupyter Notebook Server
		if _JUPYTER_SERVER_PROC is not None:
			_JUPYTER_SERVER_PROC.terminate()
			_JUPYTER_SERVER_PROC = None
		else:
			msg = 'No jupyter notebook server is running; cannot stop it'
			raise ValueError(msg)

		if _JUPYTER_KERNEL is not None:
			# Stop the Jupyter Notebook Kernel
			## - TODO: Actually stop it, don't just trust the GC.
			_JUPYTER_KERNEL = None
		else:
			msg = 'No jupyter kernel is running; cannot stop it'
			raise ValueError(msg)
