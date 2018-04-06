from library import Library
from ..nodes import Generator
from conditional import Conditional

class TabSwitch(Library):
	dependencies = ["KeyPress"]

	def __init__(self, layout):
		super(TabSwitch, self).__init__(layout)

		self.focusable = []
		self.focused_id = 0

	def loop(self, instances):
		key = instances["KeyPress"].getKey()
		if key == 9: # Tab
			self.tab(instances)

	def tab(self, instances):
		if self.focused_id >= len(self.focusable):
			self.focused_id = 0

		if self.focused_id >= len(self.focusable):
			return

		old = self.focusable[self.focused_id]

		self.focused_id += 1
		if self.focused_id >= len(self.focusable):
			self.focused_id = 0

		new = self.focusable[self.focused_id]


		if "Events" in instances:
			old.emit("blur", new)
			new.emit("focus", old)

		old.revoke()
		new.revoke()

	class Focusable(Generator):
		container = True
		text_container = False
		properties = []

		def init(self, **kwargs):
			self.layout.libs["TabSwitch"].focusable.append(self)

		def onGenerate(self):
			from ..xml_parser import handleElement

			if len(self.children) != 1:
				raise ValueError("<Focusable> can contain only one node")

			slots = dict(**self.slots)
			slots["focused"] = "True" if self.layout.libs["TabSwitch"].focusable.index(self) == self.layout.libs["TabSwitch"].focused_id else "False"
			return handleElement(self.children[0], self.defines, slots, additional_nodes=self.additional_nodes, global_slots=self.global_slots)