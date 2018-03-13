from rect import Rect

class AlignRight(Rect):
	container = True
	text_container = False

	def __init__(self, width, height=None, bg=None, children=[]):
		super(AlignRight, self).__init__(width=width, height=height, bg=bg)

		if len(children) != 1:
			raise ValueError("<AlignRight> can contain only one node")

		self.child = children[0]

	def render(self, layout, dry_run=False):
		# Get child size
		child_width, child_height = self.guessContainerSize(layout)

		# Guess container size
		if self.height is None:
			height = child_height
		else:
			height = self.height

		x1, y1, x2, y2 = super(AlignRight, self).render(layout, dry_run=dry_run, height=height)
		self.renderChildren(layout, x1, y1, x2, y2, dry_run=dry_run, child_width=child_width)

		return x1, y1, x2, y2

	def guessContainerSize(self, layout):
		x1, y1, x2, y2 = super(AlignRight, self).render(layout, dry_run=True, width=self.width, height=self.height or 0)

		return self.renderChildren(layout, x1, y1, x2, y2, dry_run=True)

	def renderChildren(self, layout, x1, y1, x2, y2, dry_run=False, child_width=None):
		if child_width is not None:
			x1 = x2 - child_width

		self.child.render_offset = (x1, y1)


		self.child.render_boundary_left_top = self.render_boundary_left_top
		self.child.render_boundary_right_bottom = self.render_boundary_right_bottom


		self.child.render_boundary_left_top[0] = x1
		self.child.render_boundary_right_bottom[0] = x2

		if self.height is not None:
			self.child.render_boundary_left_top[1] = y1
			self.child.render_boundary_right_bottom[1] = y2


		self.child.parent = self
		self.child.render_stretch = self.render_stretch

		child_x1, child_y1, child_x2, child_y2 = self.child.render(layout, dry_run=dry_run)

		return child_x2 - child_x1, child_y2 - child_y1