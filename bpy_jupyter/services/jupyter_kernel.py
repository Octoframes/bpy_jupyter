import threading

import jupyter_server.serverapp
from ipykernel.kernelapp import IPKernelApp


class CustomServerApp(jupyter_server.serverapp.ServerApp):
	def initialize(self, argv=None):
		super().initialize(argv)


def start_jupyter_server():
	server_app = CustomServerApp()
	server_app.initialize(
		[
			'--ip',
			'127.0.0.6',
			'--port',
			'8888',
			'--no-browser',
		]
	)
	server_app.start()


_JUPYTER_THREAD: threading.Thread | None = None
_LOCK: threading.Lock = threading.Lock()


def is_kernel_running():
	with _LOCK:
		return _JUPYTER_THREAD is not None


def start_kernel():
	global _JUPYTER_THREAD
	with _LOCK:
		if _JUPYTER_THREAD is None:
			jupyter_kernel = IPKernelApp.instance()
			jupyter_kernel.initialize(
				['python']  # + RUNTIME_CONFIG['args']
			)
			jupyter_kernel.kernel.start()  # kernelApp.start() is what actually starts it.

			# start_jupyter_server()
			_JUPYTER_THREAD = jupyter_kernel
		else:
			msg = f'A kernel is already running: {_JUPYTER_THREAD}'
			raise ValueError(msg)


def stop_kernel():
	global _JUPYTER_THREAD
	with _LOCK:
		if _JUPYTER_THREAD is not None:
			# _JUPYTER_THREAD.stop()
			_JUPYTER_THREAD = None
		else:
			msg = 'No kernel is running; cannot stop'
			raise ValueError(msg)
