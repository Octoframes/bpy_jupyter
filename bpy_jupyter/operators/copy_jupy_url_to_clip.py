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

"""Defines the `CopyJupyURLToClip` operator.

Inspired by <https://github.com/cheng-chi/blender_notebook/blob/master/blender_notebook/kernel.py>
"""

import datetime
import ipaddress
import secrets

import bpy
import pyperclipfix

from ..services import jupyter_kernel as jkern
from ..types import BLOperatorStatus, OperatorType

####################
# - Constants
####################
CLIPBOARD_CLEAR_DELAY = 45


####################
# - Constants
####################
class CopyJupyURLToClip(bpy.types.Operator):
	"""Copy a Jupyter Server URL to the system clipboard. The system clipboard will be cleared after a timeout, unless otherwise altered."""

	bl_idname = OperatorType.CopyJupyURLToClip
	bl_label = 'Copy Jupyter Server URL'

	_timer = None
	_start_time = None
	url_type: bpy.props.EnumProperty(
		name='Jupyter URL Type',
		description='The type of Jupyter URL to copy to the clipboard.',
		items=[
			(
				'API',
				'API Server',
				'The API server, which allows connections from any Jupyter client.',
			),
			(
				'LAB',
				'Lab Server',
				'The Lab server, which provides a browser-based IDE.',
			),
		],
		default='API',
	)

	def jupyter_url(
		self,
		jupyter_ip: ipaddress.IPv4Address | ipaddress.IPv6Address,
		jupyter_port: int,
	) -> str:
		match self.url_type:
			case 'API':
				return jkern.jupyter_api_url(jupyter_ip, jupyter_port)
			case 'LAB':
				return jkern.jupyter_lab_url(jupyter_ip, jupyter_port)

		msg = 'URL Type not valid'
		raise ValueError(msg)

	@classmethod
	def poll(cls, _: bpy.types.Context) -> bool:
		return jkern.is_kernel_running()

	def modal(
		self, context: bpy.types.Context, event: bpy.types.Event
	) -> BLOperatorStatus:
		if (
			event.type == 'TIMER'
			and (datetime.datetime.now() - self._start_time).seconds
			> CLIPBOARD_CLEAR_DELAY // 2
		):
			# Stop the Timer
			wm = context.window_manager
			wm.event_timer_remove(self._timer)
			self._timer = None
			self.start_time = None

			# Clear Clipboard
			## - ONLY if the clipboard still contains our token.
			## - This helps prevent interfering with the user's life.
			clipboard: str = pyperclipfix.paste()
			if secrets.compare_digest(
				clipboard,
				self.jupyter_url(
					ipaddress.IPv4Address(context.scene.jupyter_ip),
					context.scene.jupyter_port,
				),
			):
				pyperclipfix.copy(' ')
				self.report(
					{'INFO'},
					'Cleared System Clipboard',
				)

			return {'FINISHED'}
		return {'PASS_THROUGH'}

	def execute(self, _: bpy.types.Context) -> BLOperatorStatus:
		# Setup Timer
		wm = context.window_manager
		self._timer = wm.event_timer_add(CLIPBOARD_CLEAR_DELAY, window=context.window)
		wm.modal_handler_add(self)

		self._start_time = datetime.datetime.now()

		# Set System Clipboard to Jupyter Server URL
		pyperclipfix.copy(
			self.jupyter_url(
				ipaddress.IPv4Address(context.scene.jupyter_ip),
				context.scene.jupyter_port,
			)
		)
		self.report(
			{'INFO'},
			f'Copied URL to System Clipboard. Will clear in {CLIPBOARD_CLEAR_DELAY} seconds.',
		)

		return {'RUNNING_MODAL'}

	def cancel(self, _: bpy.types.Context) -> None:
		# Stop the Timer
		wm = context.window_manager
		wm.event_timer_remove(self._timer)
		self._timer = None
		self.start_time = None


####################
# - Blender Registration
####################
BL_REGISTER = [CopyJupyURLToClip]
