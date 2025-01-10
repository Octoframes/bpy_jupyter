"""Provides a '@staticproperty', which is like '@property', but static. It can be very useful in specific situations."""

import typing as typ


class staticproperty(property):  # noqa: N801
	"""A read-only variant of `@property` that is entirely static, for use in specific situations.

	The decorated method must take no arguments whatsoever, including `self`/`cls`.

	Examples:
		Exactly as you'd expect.
		```python
		class Spam:
			@staticproperty
			def eggs():
				return 10

		assert Spam.eggs == 10
		```
	"""

	def __get__(self, instance: typ.Any, owner: type | None = None) -> typ.Any:
		"""Overridden getter that ignores instance and owner, and just returns the value of the evaluated (static) method.

		Returns:
			The evaluated value of the static method that was decorated.
		"""
		return self.fget()  # type: ignore
		## .fget() is guaranteed to exist by @property, so we can safely ignore the type.
