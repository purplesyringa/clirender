from library import Library
from ..nodes import Generator

class Conditional(Library):
	def __init__(self, layout):
		super(Conditional, self).__init__(layout)


	class If(Generator):
		container = True
		text_container = False

		def init(self, is_, with_=None, then=None, else_=None):
			self.is_ = is_
			self.with_ = with_
			self.then = then
			self.else_ = else_

			if self.with_ is None:
				if then is not None:
					raise ValueError("Unexpected 'then' argument of <If>")
				elif else_ is not None:
					raise ValueError("Unexpected 'else' argument of <If>")
			else:
				if then is None:
					raise ValueError("Expected 'then' argument of <If with>")
				elif else_ is None:
					raise ValueError("Expected 'else' argument of <If with>")

		def onGenerate(self):
			from ..xml_parser import handleElement

			result = self.evaluate()

			if self.with_ is None:
				# <If is="condition">
				#   <Then>
				#     <A />
				#   </Then>
				#   <Else>
				#     <B />
				#   </Else>
				# </If>

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
			else:
				# <If with="slot" is="condition" then="A" else="B">
				#   <Slot name="slot" />
				# </If>

				slots = dict(**self.slots)
				if result:
					slots[self.with_] = self.then
				else:
					slots[self.with_] = self.else_

				res = []
				for child in self.children:
					if child.tag == ("Then", "Else"):
						raise ValueError("Unexpected %s inside <If with>" % child)

					res += handleElement(child, self.defines, slots, self.additional_nodes)

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