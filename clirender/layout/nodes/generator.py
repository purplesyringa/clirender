class Generator(object):
	container = False
	text_container = False

	def __init__(self, children=[], **kwargs):
		self.children = children

	def get(self, attr):
		from ..slot import Slot

		value = getattr(self, attr)
		while isinstance(value, Slot):
			value = value.evaluate()

		if callable(value):
			value = value()

		return value

	def generate(self):
		raise NotImplementedError