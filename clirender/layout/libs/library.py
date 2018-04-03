class Library(object):
	def __init__(self, layout):
		self.layout = layout

def Slot(name, wrapped=False):
	def wrapper(fn):
		def slot(*args, **kwargs):
			return fn(*args, **kwargs)

		slot.slot = name
		slot.wrapped = wrapped
		return slot

	return wrapper

def patch(obj):
	def wrapper(cls):
		if not isinstance(cls, type):
			raise TypeError("Can only @patch a class")

		names = set(dir(cls)) # All variables
		names -= set(dir(type)) # Remove some __vars__
		if "__weakref__" in names:
			names.remove("__weakref__") # Remove __weakref__

		for name in names:
			setattr(obj, name, getattr(cls, name))

		return obj

	return wrapper