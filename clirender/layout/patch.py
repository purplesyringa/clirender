class PatchProxy(object):
	def __init__(self, instance):
		object.__setattr__(self, "cls", instance._patched_obj)
		object.__setattr__(self, "instance", instance)

	def __getattribute__(self, name):
		cls = object.__getattribute__(self, "cls")
		instance = object.__getattribute__(self, "instance")

		if name in cls._unpatched:
			value = cls._unpatched[name]
		else:
			value = getattr(cls, name)

		if callable(value) and value.__self__ is None:
			# Unbound
			value = value.__get__(instance, cls)

		return value

	def __setattr__(self, name, value):
		cls = object.__getattribute__(self, "cls")
		instance = object.__getattribute__(self, "instance")

		if name in instance._unpatched:
			instance._unpatched[name] = value
		else:
			setattr(cls, name, value)


def patch(*objects):
	def wrapper(cls):
		if not isinstance(cls, type):
			raise TypeError("Can only @patch a class")

		names = set(dir(cls)) # All variables
		names -= set(dir(type)) # Remove some __vars__
		if "__weakref__" in names:
			names.remove("__weakref__") # Remove __weakref__

		# Bring back some methods defined by type()
		names.add("__init__")

		for obj in objects:
			if not hasattr(obj, "_unpatched"):
				obj._unpatched = {}
				obj._patched_obj = obj

			for name in names:
				if name not in cls.__dict__:
					continue

				if name not in obj._unpatched and hasattr(obj, name):
					obj._unpatched[name] = getattr(obj, name)

				setattr(obj, name, cls.__dict__[name])

		return obj

	return wrapper


patch.super = PatchProxy