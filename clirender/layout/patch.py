class PatchProxy(object):
	def __init__(self, cls, instance):
		object.__setattr__(self, "cls", cls)
		object.__setattr__(self, "basecls", type(instance)._patched_obj)
		object.__setattr__(self, "instance", instance)

	def __getattribute__(self, name):
		cls = object.__getattribute__(self, "cls")
		basecls = object.__getattribute__(self, "basecls")
		instance = object.__getattribute__(self, "instance")

		value = getattr(basecls, name)
		if name in basecls._unpatched:
			unpatched = basecls._unpatched[name]
			idx = unpatched.index(cls)
			if idx == 0:
				raise AttributeError("patch.super() cannot be called in base class. Use super() instead.")
			elif idx == 1:
				value = unpatched[0] # ID 0 is a method, not class
				if value is None:
					raise AttributeError("%s is not defined in super class %s" % (name, basecls))
			else:
				value = unpatched[idx - 1].__dict__[name]

		if callable(value):
			# Unbound
			value = value.__get__(instance, basecls)

		return value

	def __setattr__(self, name, value):
		raise ValueError("patch.super() doesn't support attribute setting.")


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

				if name not in obj._unpatched:
					if hasattr(obj, name):
						obj._unpatched[name] = [getattr(obj, name)]
					else:
						obj._unpatched[name] = [None]

				obj._unpatched[name].append(cls)

				setattr(obj, name, cls.__dict__[name])

		return cls

	return wrapper


patch.super = PatchProxy