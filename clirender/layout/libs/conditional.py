from library import Library
from ..nodes import Generator

class Conditional(Library):
	def __init__(self, layout):
		super(Conditional, self).__init__(layout)


	class If(Generator):
		container = True
		text_container = False

		def init(self, is_=None):
			self.is_ = is_

		def onGenerate(self):
			from ..xml_parser import handleElement

			result = self.evaluate()

			res = []
			for child in self.children:
				if child.tag == "Then":
					if result:
						res += handleElement(child, self.defines, self.slots, self.additional_nodes)
				elif child.tag == "Else":
					if not result:
						res += handleElement(child, self.defines, self.slots, self.additional_nodes)
				else:
					raise ValueError("Unexpected %s inside <If>" % child)

			return res

		def evaluate(self):
			scope = {}
			for handler in Conditional.handlers:
				scope.update(handler(self))

			try:
				value = eval(self.is_, scope)
			except KeyError, e:
				raise ValueError("Unknown variable used in conditional: %s" % e[0])
			return bool(value)


	class _Inside(Generator):
		container = True
		text_container = False

		def onGenerate(self):
			from ..xml_parser import handleElement

			res = []
			for child in self.children:
				res += handleElement(child, self.defines, self.slots, self.additional_nodes)

			return res

	class Then(_Inside):
		pass
	class Else(_Inside):
		pass


	handlers = []
	@staticmethod
	def add(handler):
		Conditional.handlers.append(handler)