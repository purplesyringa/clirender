from library import Library
from ..nodes import Generator
from conditional import Conditional
from keypress import KeyCodes, Ctrl

class TabSwitch(Library):
	dependencies = ["KeyPress"]

	def __init__(self, layout):
		super(TabSwitch, self).__init__(layout)

		self.focusable = []
		self.focused = None

	def loop(self, instances):
		key = instances["KeyPress"].getKey()
		if key == KeyCodes.Tab: # Tab
			self.tab(instances, backward=False)
		elif key == Ctrl(KeyCodes.Tab): # Ctrl+Tab
			self.tab(instances, backward=True)
		else:
			if self.focused:
				self.focused.emit("keyPress", recursive=True, key=key)

	def tab(self, instances, backward=False):
		if len(self.focusable) == 0:
			return

		old = self.focused or self.focusable[0]
		index = self.focusable.index(old)

		if backward:
			index -= 1
			if index < 0:
				index = len(self.focusable) - 1
		else:
			index += 1
			if index >= len(self.focusable):
				index = 0

		self.focused = self.focusable[index]


		if "Events" in instances:
			old         .emit("blur",  new=self.focused)
			self.focused.emit("focus", old=old         )

		old         .revoke()
		self.focused.revoke()

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


			TabSwitchInstance = self.layout.libs["TabSwitch"]

			slots = dict(**self.slots)
			slots["focused"] = self is (TabSwitchInstance.focused or TabSwitchInstance.focusable[0])
			return handleElement(self.children[0], self.defines, slots, additional_nodes=self.additional_nodes, global_slots=self.global_slots)