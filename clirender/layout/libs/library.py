class Library(object):
	def __init__(self, layout):
		self.layout = layout

def Slot(name):
	def wrapper(fn):
		def slot(*args, **kwargs):
			return fn(*args, **kwargs)

		slot.slot = name
		return slot

	return wrapper