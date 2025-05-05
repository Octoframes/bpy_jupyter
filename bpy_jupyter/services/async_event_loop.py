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

"""Manages an `asyncio` event loop, which allows running asynchronous extension code in the main thread of Blender.

## Motivation: Waiting for Godo... Something to Happen
Blender's Python API is not thread safe, meaning that the main thread must be used to update all ex. properties, UI elements, etc. .
At the same time, when Python code runs in Blender's main thread, the UI becomes unresponsive until it is finished.
What to do?

Of course, many salient use cases **require** interacting with the main thread, yet **do not constantly require** the CPU's attention:

- **Network Client**: Waiting for responses from a network server, after making a request.
	- For instance, a progress bar that responds to updates from a cloud-service ex. a render farm, expensive physics simulation, etc. .
- **Network Server**: Waiting for clients to connect to us,
	- For instance, a mini web-service enabling IDE shortcuts that trigger actions within a running Blender.
- **Input Processing**: Waiting for input from some kind of input device.
	- For instance, an addon that maps game controller buttons to Blender properties, or MIDI sliders to rig properties.
- **IPC**: Waiting for status updates from an external process, started via ex. `subprocess` or `multiprocessing`.
	- For instance, monitoring a computationally heavy external command - or simply switching between light/dark mode in response to theming signals on a Linux system's `dbus`!

By inelegantly slapping an `asyncio` event loop on top of Blender's main thread, any code that spends most of its time "just waiting" can now `await` whatever it needs to, without blocking Blender's main thread.

## Limitations
It's worth saying: **Concurrency is not parallelism**.

When using this system, _all `async` code still runs in the main thread_.
If that code uses a lot of CPU processing, then **it will block that main thread and freeze Blender's UI**.

To run expensive code "in the background", one should use the right tools for the job, such as `multiprocessing`.
The `async` part only comes into play when ex. `await`ing messages from that external process to update the extension's UI.


Attributes:
	EVENT_LOOP_TIMEOUT_SEC: Number of seconds between each iteration of the `asyncio` event loop.
"""

import asyncio

import bpy

####################
# - Constants
####################
EVENT_LOOP_TIMEOUT_SEC = 0.001


####################
# - Event Loop
####################
@bpy.app.handlers.persistent
def increment_event_loop() -> float:
	"""Run one iteration of the `asyncio` event loop.

	## Mechanism
	The hack at work here is thus: Blender's event loop is asked to increment the `asyncio` event loop "very often".

	Each time `increment_event_loop` is called, all pending (non-`await`ing) tasks will run until they either finish, or reach an `await`.
	This is the meaning of "one iteration", and this is achieved using `loop.call_soon(loop.stop)`, then `loop.run_forever()`.

	Since the event loop retains its state, and ability to accept tasks, after `loop.stop()`, doing this repeatedly amounts to a frequently invoked "pause and flush".

	Notes:
		**To enable**, use `bpy.app.timers.register(..., persistent=True)`.

	Returns:
		The number of seconds to wait before running this function again.
	"""
	loop = asyncio.get_event_loop()
	_ = loop.call_soon(loop.stop)
	loop.run_forever()

	return EVENT_LOOP_TIMEOUT_SEC


####################
# - Start
####################
def start() -> None:
	"""Start the `asyncio` event loop.

	Notes:
		Registers `increment_event_loop` to `bpy.app.timers`.

		**DO NOT** run if an event loop has already been started using `start()`.
	"""
	bpy.app.timers.register(increment_event_loop, persistent=True)  # pyright: ignore[reportUnknownMemberType]


def stop():
	"""Stop a running `asyncio` event loop.

	Notes:
		Unregisters `increment_event_loop` from `bpy.app.timers`.

		**DO NOT** run if an event loop has not already been started using `start()`.
	"""
	bpy.app.timers.unregister(increment_event_loop)  # pyright: ignore[reportUnknownMemberType]
