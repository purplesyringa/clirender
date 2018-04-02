from library import Library
from ..nodes import Generator, Container

class Loops(Library):
	class Range(Generator):
		container = True
		text_container = False

		def init(self, from_, to, step=1, slot=None):
			self.from_ = from_
			self.to = to
			self.step = step
			self.slot = slot

		def onGenerate(self):
			from ..xml_parser import handleElement

			try:
				from_ = int(self.from_)
			except ValueError:
				raise ValueError("'from' attribute of <Range> must be an integer")

			try:
				to = int(self.to)
			except ValueError:
				raise ValueError("'to' attribute of <Range> must be an integer")

			try:
				step = int(self.step)
			except ValueError:
				raise ValueError("'step' attribute of <Range> must be an integer")

			to += step

			new_slots = dict(**self.slots)

			res = []
			for i in range(from_, to, step):
				if self.slot is not None:
					new_slots[self.slot] = i

				for child in self.children:
					res += handleElement(child, self.defines, dict(**new_slots), additional_nodes=self.additional_nodes, global_slots=self.global_slots)

			return res

	class For(Generator):
		container = True
		text_container = False

		def init(self, in_, slot=None):
			self.in_ = in_
			self.slot = slot

		def onGenerate(self):
			from ..xml_parser import handleElement

			try:
				in_ = list(self.in_)
			except ValueError:
				raise ValueError("'in' attribute of <For> must be a list")

			new_slots = dict(**self.slots)

			res = []
			for i in in_:
				if self.slot is not None:
					new_slots[self.slot] = i

				for child in self.children:
					res += handleElement(child, self.defines, dict(**new_slots), additional_nodes=self.additional_nodes, global_slots=self.global_slots)

			return res