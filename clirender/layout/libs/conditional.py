from library import Library
from ..nodes import Generator
import numexpr

class Conditional(Library):
	def __init__(self, layout):
		super(Conditional, self).__init__(layout)


	class If(Generator):
		container = True
		text_container = False

		def __init__(self, is_=None, children=[]):
			super(Conditional.If, self).__init__(children=children)

			self.is_ = is_

		def generate(self, defines, additional_nodes):
			from ..xml_parser import handleElement

			result = self.evaluate()

			res = []
			for child in self.children:
				if child.tag == "Then":
					if result:
						res += handleElement(child, defines, self.slots, additional_nodes)
				elif child.tag == "Else":
					if not result:
						res += handleElement(child, defines, self.slots, additional_nodes)
				else:
					raise ValueError("Unexpected %s inside <If>" % child)

			return res

		def evaluate(self):
			scope = {}
			for handler in Conditional.handlers:
				scope.update(handler(self))

			try:
				value = numexpr.evaluate(self.is_, local_dict={}, global_dict=scope).item()
			except KeyError, e:
				raise ValueError("Unknown variable used in conditional: %s" % e[0])
			return bool(value)


	class _Inside(Generator):
		container = True
		text_container = False

		def __init__(self, children=[]):
			super(Conditional._Inside, self).__init__(children=children)

		def generate(self, defines, additional_nodes):
			from ..xml_parser import handleElement

			res = []
			for child in self.children:
				res += handleElement(child, defines, self.slots, additional_nodes)

			return res

	class Then(_Inside):
		pass
	class Else(_Inside):
		pass


	handlers = []
	@staticmethod
	def add(handler):
		Conditional.handlers.append(handler)