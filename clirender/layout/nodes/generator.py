class Generator(object):
	container = False
	text_container = False

	def __init__(self, slots, children=[], **kwargs):
		self.children = children
		self.slots = slots
		self._cached = None

		self.init(**kwargs)

	def init(self):
		pass

	def generate(self):
		raise NotImplementedError


	def revoke(self):
		self._cached = None