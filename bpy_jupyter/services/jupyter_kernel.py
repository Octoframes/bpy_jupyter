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

"""Manages a global instance of an embedded `ipython` kernel, as implemented by `bpy_jupyter.utils.IPyKernel`.

Notes:
	**Must** be used together with `bpy_jupyter.services.async_event_loop`, or some other implementation of an `asyncio` event loop.

	If this is not done, then the embedded kernel will be unable to act on incoming requests.
	Instead, such requests will hang forever / until timing out.

Attributes:
	IPYKERNEL: Wrapper for an instance of the embedded `ipython` kernel.
"""

from pathlib import Path

from ..utils.ipykernel import IPyKernel

####################
# - Globals
####################
IPYKERNEL: IPyKernel | None = None


####################
# - Lifecycle
####################
def init(*, path_connection_file: Path) -> None:
	"""Initialize the IPyKernel using the given connection file path.

	Notes:
		This is merely a setup function.

		The kernel is not actually started until `IPYKERNEL.start()` is called.

	Parameters:
		path_connection_file: Path to the kernel connection file.
	"""
	global IPYKERNEL  # noqa: PLW0603

	if IPYKERNEL is None or not IPYKERNEL.is_running:
		IPYKERNEL = IPyKernel(path_connection_file=path_connection_file)  # pyright: ignore[reportConstantRedefinition]

	elif IPYKERNEL.is_running:
		msg = "Can't re-initialize `IPYKERNEL`, since it is running."
		raise ValueError(msg)


####################
# - Information
####################
def is_kernel_running() -> bool:
	"""Whether the kernel is both initialized and running.

	Notes:
		Use this to check the kernel state from `poll()` methods, since it also takes the uninitialized `IPYKERNEL is None` state into account.

	Returns:
		Whether the underlying `IPYKERNEL` is both initialized (aka. not `None`), and running (aka. `IPYKERNEL.is_running`).
	"""
	return IPYKERNEL is not None and IPYKERNEL.is_running
