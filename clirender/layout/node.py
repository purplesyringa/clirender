class Node(object):
	container = False
	text_container = False

	def __init__(self, children=None, **kwargs):
		self.render_offset = (None, None)
		self.render_boundary_left_top = [None, None]
		self.render_boundary_right_bottom = [None, None]
		self.parent = None
		self.render_stretch = None

		self.inheritable = {}

		self.children = children

	def render(self, layout, dry_run=False):
		raise NotImplementedError

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
			return value

		return value


	def getChildren(self):
		from generator import Generator

		res = []
		for child in self.children:
			if isinstance(child, Generator):
				res += child.generate()
			else:
				res.append(child)

		return res