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