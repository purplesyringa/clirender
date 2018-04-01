from library import Library
from ..nodes import Generator
from conditional import Conditional

def handler(node):
	return dict(focused=True)

Conditional.add(handler)

class TabSwitch(Library):
	dependencies = ["KeyPress"]
	focusable = []
	focused_id = 0

	def __init__(self, layout):
		super(TabSwitch, self).__init__(layout)

	def loop(self, instances):
		key = instances["KeyPress"].getKey()
		if key == 9: # Tab
			self.tab()

	def tab(self):
		TabSwitch.focused_id += 1
		if TabSwitch.focused_id >= len(TabSwitch.focusable):
			TabSwitch.focused_id = 0

	class Focusable(Generator):
		container = True
		text_container = False

		def __init__(self, **kwargs):
			super(TabSwitch.Focusable, self).__init__(**kwargs)
			TabSwitch.focusable.append(self)

		def generate(self):
			from ..xml_parser import handleElement

			if len(self.children) != 1:
				raise ValueError("<Focusable> can contain only one node")

			slots = dict(**self.slots)
			slots["focused"] = "True" if TabSwitch.focusable.index(self) == TabSwitch.focused_id else "False"
			return handleElement(self.children[0], self.defines, slots, additional_nodes=self.additional_nodes)