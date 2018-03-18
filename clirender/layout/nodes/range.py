from generator import Generator
from container import Container

class Range(Generator):
	container = True
	text_container = False

	def __init__(self, from_, to, step=1, slot=None, children=[]):
		super(Range, self).__init__(children=children)

		self.from_ = from_
		self.to = to
		self.step = step
		self.slot = slot

	def generate(self):
		try:
			from_ = int(self.get("from_"))
		except ValueError:
			raise ValueError("'from' attribute of <Range> must be an integer")

		try:
			to = int(self.get("to"))
		except ValueError:
			raise ValueError("'to' attribute of <Range> must be an integer")

		try:
			step = int(self.get("step"))
		except ValueError:
			raise ValueError("'step' attribute of <Range> must be an integer")

		new_slots = dict(**self.slot_context)

		res = []
		for i in range(from_, to, step):
			if self.get("slot") is not None:
				new_slots[self.get("slot")] = str(i)

			for pos, child in enumerate(self.children):
				container = Container(children=[child])
				container.type = "range"
				container.range_value = i
				container.range_begin = pos == 0

				container.slot_context = dict(**new_slots)
				container.inherit_slots = False

				res.append(container)

		return res