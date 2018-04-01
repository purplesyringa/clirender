from library import Library
from ..nodes import Generator, Container

class Range(Library):
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

			new_slots = dict(**self.slots)

			res = []
			for i in range(from_, to, step):
				if self.slot is not None:
					new_slots[self.slot] = str(i)

				for child in self.children:
					res += handleElement(child, self.defines, dict(**new_slots), additional_nodes=self.additional_nodes)

			return res