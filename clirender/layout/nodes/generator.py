class Generator(object):
	container = False
	text_container = False

	def __init__(self, children=[], **kwargs):
		self.children = children

	def generate(self):
		raise NotImplementedError