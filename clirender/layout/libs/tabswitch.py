from library import Library
from ..nodes import Generator
from conditional import Conditional
from keypress import KeyCodes, Ctrl

class TabSwitch(Library):
	dependencies = ["KeyPress"]

	def __init__(self, layout):
		super(TabSwitch, self).__init__(layout)

		self._focusable = []
		self.focused = None

	@property
	def focusable(self):
		return [node for node in self._focusable if not node.disabled]

	def getFocused(self):
		if self.focused in self.focusable:
			return self.focused
		elif len(self.focusable) > 0:
			return self.focusable[0]
		else:
			return None


	def loop(self, instances):
		key = instances["KeyPress"].getKey()
		if key == KeyCodes.Tab: # Tab
			self.tab(instances, backward=False)
		elif key == Ctrl(KeyCodes.Tab): # Ctrl+Tab
			self.tab(instances, backward=True)
		else:
			focused = self.getFocused()
			if focused is not None:
				focused.emit("keyPress", recursive=True, key=key)

	def tab(self, instances, backward=False):
		old = self.getFocused()
		if old is None:
			return

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

		def init(self, disabled=False):
			self.disabled = disabled != False

			self.layout.libs["TabSwitch"]._focusable.append(self)

		def onGenerate(self):
			from ..xml_parser import handleElement

			if len(self.children) != 1:
				raise ValueError("<Focusable> can contain only one node")


			TabSwitchInstance = self.layout.libs["TabSwitch"]

			slots = dict(**self.slots)
			slots["focused"] = self is TabSwitchInstance.getFocused()
			return handleElement(self.children[0], self.defines, slots, additional_nodes=self.additional_nodes, global_slots=self.global_slots)

		def onDestroy(self):
			lst = self.layout.libs["TabSwitch"]._focusable
			if self in lst:
				lst.remove(self)