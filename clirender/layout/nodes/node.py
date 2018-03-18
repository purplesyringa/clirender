class Node(object):
	container = False
	text_container = False

	def __init__(self, children=None, value=[], **kwargs):
		self.render_offset = (None, None)
		self.render_boundary_left_top = [None, None]
		self.render_boundary_right_bottom = [None, None]
		self.parent = None
		self.render_stretch = None

		self.slot_context = {}
		self.inheritable = {}

		self.children = children
		self.value = value

	def render(self, layout, dry_run=False):
		raise NotImplementedError

	def get(self, attr):
		from ..slot import Slot

		value = getattr(self, attr)
		while isinstance(value, Slot):
			value = value.evaluate()

		if callable(value):
			value = value()

		return value

	def getValue(self):
		from ..slot import Slot

		res = ""
		for part in self.value:
			while isinstance(part, Slot):
				part = part.evaluate()

			res += part

		return res

	def inherit(self, attr):
		node = self

		value = getattr(node, attr, None)
		try:
			while value.strip().lower() == "inherit":
				parent = node.parent
				if parent is None:
					return None

				value = getattr(parent, attr, None)
				if value is None:
					value = parent.inheritable.get(attr, None)

				# Bypass <Container>
				from container import Container
				if value is None and isinstance(parent, Container):
					value = "inherit"

				node = parent
		except AttributeError:
			pass

		from ..slot import Slot
		while isinstance(value, Slot):
			value = value.evaluate()

		try:
			if isinstance(value, Node) and value.strip().lower() == "inherit":
				return value.inherit(attr)
		except AttributeError:
			pass

		return value


	def getChildren(self):
		from generator import Generator

		res = []
		for child in self.children:
			if isinstance(child, Generator):
				child.slot_context = self.slot_context
				res += child.generate()
			else:
				res.append(child)

		return res


	def renderChild(self, layout, child, dry_run, offset, boundary_left_top, boundary_right_bottom, stretch):
		from ..slot import Slot
		if isinstance(child, Slot):
			node = child.evaluate()
			if isinstance(node, str) or isinstance(node, unicode):
				raise ValueError("Cannot render text inside a node")

			node["node"].slot_context = node["context"].slot_context
			node["node"].inherit_slots = False

			return self.renderChild(
				layout, node["node"], dry_run=dry_run,

				offset=offset,
				boundary_left_top=boundary_left_top,
				boundary_right_bottom=boundary_right_bottom,
				stretch=stretch
			)

		child.render_offset = offset
		child.render_boundary_left_top = boundary_left_top
		child.render_boundary_right_bottom = boundary_right_bottom
		child.render_stretch = stretch
		child.parent = self
		if getattr(child, "inherit_slots", True):
			child.slot_context = self.slot_context

		return child.render(layout, dry_run=dry_run)