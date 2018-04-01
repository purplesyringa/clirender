class Generator(object):
	container = False
	text_container = False

	def __init__(self, slots, children=[], **kwargs):
		self.children = children
		self.slots = slots

	def generate(self):
		raise NotImplementedError