from element import Element

class Node(Element):
	container = False
	text_container = False

	def __init__(self, slots, elem, children=None, value=[], ref=None, **kwargs):
		super(Node, self).__init__(ref=ref)

		self.render_offset = (None, None)
		self.render_plus_size = (None, None)
		self.render_boundary_left_top = [None, None]
		self.render_boundary_right_bottom = [None, None]
		self.parent = None
		self.gen_parent = None
		self.render_stretch = None

		self.inheritable = {}

		self._children = children
		self.value = value
		self.slots = slots
		self.elem = elem
		self._revoked = False
		self._completely_revoked = False
		self._changed = False
		self.cache_sizes = (None, None)
		self.cache_offset = (None, None)

		self._kwargs = kwargs
		self._initted = False

	@property
	def children(self):
		return self._get_children(self._children, self)

	@children.setter
	def children(self, children):
		self._children = children

	def _get_children(self, old, gen_parent):
		from generator import Generator

		children = []
		for child in old:
			child.parent = self
			child.gen_parent = gen_parent

			if isinstance(child, Generator):
				child.layout = self.layout
				generated = child.generate()

				for subchild in self._get_children(generated, child):
					if not hasattr(subchild, "generated_by"):
						subchild.generated_by = []
					subchild.generated_by.append(child)

					children.append(subchild)
			else:
				children.append(child)

		return children


	def onRender(self, *args, **kwargs):
		raise NotImplementedError

	def render(self, cls=None, **kwargs):
		if not self._initted:
			self.runInit(**self._kwargs)
			self._initted = True

		obj = self if cls is None else super(cls, self)
		return obj.onRender(**kwargs)


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

		try:
			if isinstance(value, Node) and value.strip().lower() == "inherit":
				return value.inherit(attr)
		except AttributeError:
			pass

		return value


	def renderChild(self, child, dry_run, offset, boundary_left_top, boundary_right_bottom, parent_width, parent_height, stretch, completely_revoked=True, plus_size=(0, 0)):
		child.cache_offset = child.render_offset
		child.cache_plus_size = child.render_plus_size

		child.render_offset = offset
		child.render_plus_size = plus_size
		child.render_boundary_left_top = boundary_left_top
		child.render_boundary_right_bottom = boundary_right_bottom
		child.render_stretch = stretch
		child.render_parent_width = parent_width
		child.render_parent_height = parent_height
		child.layout = self.layout
		child._completely_revoked = child._changed or completely_revoked
		child._changed = False

		sizes = child.render(dry_run=dry_run)
		child._revoked = False

		child.cache_sizes = sizes
		child.cache_offset = offset
		child.cache_plus_size = plus_size
		return sizes


	def getBoundaryBox(self):
		return dict(
			left=self.cache_offset[0] + self.cache_plus_size[0],
			top=self.cache_offset[1] + self.cache_plus_size[1],

			right=self.cache_offset[0] + self.cache_sizes[0],
			bottom=self.cache_offset[1] + self.cache_sizes[1],

			width=self.cache_sizes[0],
			height=self.cache_sizes[1]
		)


	def destroy(self):
		if self.container:
			for child in self._children:
				child.destroy()

		if hasattr(self, "onDestroy"):
			self.onDestroy()