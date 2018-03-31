from generator import Generator
from container import Container

class Range(Generator):
	def __init__(self, from_, to, step=1, slot=None, children=[]):
		super(Range, self).__init__(children=children)

		self.from_ = from_
		self.to = to
		self.step = step
		self.slot = slot

	def generate(self, slots, defines):
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

		new_slots = dict(**slots)

		res = []
		for i in range(from_, to, step):
			if self.slot is not None:
				new_slots[self.slot] = str(i)

			for child in self.children:
				res += handleElement(child, defines, dict(**new_slots))

		return res