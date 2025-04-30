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

import bpy

####################
# - Constants
####################
EVENT_LOOP_TIMEOUT_SEC = 0.001


####################
# - Globals
####################
IS_RUNNING: bool = False


####################
# - Event Loop
####################
@bpy.app.handlers.persistent
def increment_event_loop() -> float:
	loop = asyncio.get_event_loop()
	loop.call_soon(loop.stop)
	loop.run_forever()

	return EVENT_LOOP_TIMEOUT_SEC


####################
# - Start
####################
def start():
	global IS_RUNNING
	bpy.app.timers.register(increment_event_loop, persistent=True)
	IS_RUNNING = True


def stop():
	global IS_RUNNING
	bpy.app.timers.unregister(increment_event_loop)
	IS_RUNNING = False
