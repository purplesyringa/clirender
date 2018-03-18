class Generator(object):
	container = False
	text_container = False

	def __init__(self, children=[], **kwargs):
		self.children = children
		self.slot_context = {}

	def get(self, attr):
		from ..slot import Slot

		value = getattr(self, attr)
		while isinstance(value, Slot):
			value = value.evaluate()

		if callable(value):
			value = value()

		return value

	def getChildren(self):
		res = []
		for child in self.children:
			if isinstance(child, Generator):
				child.slot_context = self.slot_context
				res += child.generate()
			else:
				res.append(dict(node=child, slots=self.slot_context))

		return res

	def generate(self):
		raise NotImplementedError