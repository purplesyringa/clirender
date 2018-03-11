class Node(object):
	container = False
	text_container = False

	def __init__(self, **kwargs):
		self.render_offset = (None, None)
		self.render_boundary_left_top = [None, None]
		self.render_boundary_right_bottom = [None, None]
		self.parent = None
		self.render_stretch = None

		self.inheritable = {}

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

				node = parent
		except AttributeError:
			return value

		return value