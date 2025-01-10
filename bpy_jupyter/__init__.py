"""A visual DSL for electromagnetic simulation design and analysis implemented as a Blender node editor."""

from functools import reduce

from . import contracts as ct
from . import operators, panels, preferences, registration
from .utils import logger

log = logger.get(__name__)


####################
# - Load and Register Addon
####################
BL_REGISTER: list[ct.BLClass] = [
	*operators.BL_REGISTER,
	*panels.BL_REGISTER,
]

BL_HANDLERS: ct.BLHandlers = reduce(
	lambda a, b: a + b,
	[
		operators.BL_HANDLERS,
		panels.BL_HANDLERS,
	],
	ct.BLHandlers(),
)

BL_KEYMAP_ITEMS: list[ct.BLKeymapItem] = [
	*operators.BL_KEYMAP_ITEMS,
	*panels.BL_KEYMAP_ITEMS,
]


####################
# - Registration
####################
def register() -> None:
	"""Implements addon registration in a way that respects the availability of addon preferences and loggers.

	Notes:
		Called by Blender when enabling the addon.

	Raises:
		RuntimeError: If addon preferences fail to register.
	"""
	log.info('Registering Addon Preferences: %s', ct.addon.NAME)
	registration.register_classes(preferences.BL_REGISTER)

	addon_prefs = ct.addon.prefs()
	if addon_prefs is not None:
		# Update Loggers
		# - This updates existing loggers to use settings defined by preferences.
		addon_prefs.on_addon_logging_changed()

		log.info('Registering Addon: %s', ct.addon.NAME)

		registration.register_classes(BL_REGISTER)
		registration.register_handlers(BL_HANDLERS)
		registration.register_keymaps(BL_KEYMAP_ITEMS)

		log.info('Finished Registration of Addon: %s', ct.addon.NAME)
	else:
		msg = f"Addon preferences did not register for addon '{ct.addon.NAME}' - something is very wrong!"
		raise RuntimeError(msg)


def unregister() -> None:
	"""Unregisters anything that was registered by the addon.

	Notes:
		Run by Blender when disabling and/or uninstalling the addon.

		This doesn't clean `sys.modules`.
		We rely on the hope that Blender has extension-extension module isolation.
	"""
	log.info('Starting %s Unregister', ct.addon.NAME)

	registration.unregister_keymaps()
	registration.unregister_handlers()
	registration.unregister_classes()

	log.info('Finished %s Unregister', ct.addon.NAME)
