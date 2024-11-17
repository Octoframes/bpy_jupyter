import sys
import threading
from ipykernel.kernelapp import IPKernelApp

_RUNNING_KERNEL: IPKernelApp = None
_LOCK: threading.Lock = threading.Lock()


def is_kernel_running():
	with _LOCK:
		return _RUNNING_KERNEL is not None


def start_kernel():
	global _RUNNING_KERNEL
	with _LOCK:
		if _RUNNING_KERNEL is None:
			_RUNNING_KERNEL = IPKernelApp.instance()
			_RUNNING_KERNEL.initialize([sys.executable])
			_RUNNING_KERNEL.kernel.start()
			_RUNNING_KERNEL.start()

		msg = f'A kernel is already running: {_RUNNING_KERNEL}'
		raise ValueError(msg)


def stop_kernel():
	global _RUNNING_KERNEL
	with _LOCK:
		_RUNNING_KERNEL = None
