from element import Element

class Generator(Element):
	container = False
	text_container = False

	def __init__(self, slots, children=[], **kwargs):
		super(Generator, self).__init__()

		self.children = children
		self.slots = slots

		self.parent = None
		self.gen_parent = None

		self._cached = None
		self._kwargs = kwargs
		self._initted = False

	def init(self):
		pass

	def generate(self):
		if not self._initted:
			self.runInit(**self._kwargs)
			self._initted = True

		if self._cached is None:
			self._cached = self.onGenerate()

		return self._cached

	def onGenerate(self):
		raise NotImplementedError


	def revoke(self):
		if self._cached is not None:
			for child in self._cached:
				child.destroy()

		self._cached = None

		node = self.parent
		while node is not None:
			node._revoked = True
			node = node.parent


	def destroy(self):
		if self._cached is not None:
			for child in self._cached:
				child.destroy()

		if hasattr(self, "onDestroy"):
			self.onDestroy()