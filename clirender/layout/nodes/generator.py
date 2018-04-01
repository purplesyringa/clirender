class Generator(object):
	container = False
	text_container = False

	def __init__(self, slots, children=[], **kwargs):
		self.children = children
		self.slots = slots
		self._cached = None
		self._kwargs = kwargs
		self._initted = False

	def init(self):
		pass

	def generate(self):
		if not self._initted:
			self.init(**self._kwargs)
			self._initted = True

		return self.onGenerate()

	def onGenerate(self):
		raise NotImplementedError


	def revoke(self):
		self._cached = None