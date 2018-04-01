from rect import Rect

class AlignRight(Rect):
	container = True
	text_container = False

	def __init__(self, width, height=None, bg=None, children=[]):
		super(AlignRight, self).__init__(width=width, height=height, bg=bg, children=children)

	def render(self, dry_run=False):
		if len(self.children) != 1:
			raise ValueError("<AlignRight> can contain only one node")

		# Get child size
		child_width, child_height = self.guessContainerSize()

		# Guess container size
		if self.height is None:
			height = child_height
		else:
			height = self.height

		x1, y1, x2, y2 = super(AlignRight, self).render(dry_run=dry_run, height=height)
		self.renderChildren(x1, y1, x2, y2, dry_run=dry_run, child_width=child_width)

		return x1, y1, x2, y2

	def guessContainerSize(self):
		x1, y1, x2, y2 = super(AlignRight, self).render(dry_run=True, width=self.width, height=self.height or 0)

		return self.renderChildren(x1, y1, x2, y2, dry_run=True)

	def renderChildren(self, x1, y1, x2, y2, dry_run=False, child_width=None):
		if child_width is not None:
			x1 = x2 - child_width

		child = self.children[0]
		child_x1, child_y1, child_x2, child_y2 = self.renderChild(
			child, dry_run=dry_run,

			offset=(x1, y1),

			boundary_left_top=(
				x1,
				y1 if self.height is not None else self.render_boundary_left_top[1]
			),
			boundary_right_bottom=(
				x2,
				y2 if self.height is not None else self.render_boundary_right_bottom[1]
			),

			stretch=self.render_stretch
		)

		return child_x2 - child_x1, child_y2 - child_y1