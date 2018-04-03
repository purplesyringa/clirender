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

		width, height = super(AlignRight, self).render(dry_run=dry_run, height=height)
		x2, y2 = self.render_offset[0] + width, self.render_offset[1] + height
		self.renderChildren(x2, y2, dry_run=dry_run, child_width=child_width)

		return width, height

	def guessContainerSize(self):
		width, height = super(AlignRight, self).render(dry_run=True, width=self.width, height=self.height or 0)
		x2, y2 = self.render_offset[0] + width, self.render_offset[1] + height

		return self.renderChildren(x2, y2, dry_run=True)

	def renderChildren(self, x2, y2, dry_run=False, child_width=None):
		x1, y1 = self.render_offset

		if child_width is not None:
			x1 = x2 - child_width

		child = self.children[0]
		return self.renderChild(
			child, dry_run=dry_run,

			offset=(x1, y1),

			boundary_left_top=[
				x1,
				y1 if self.height is not None else self.render_boundary_left_top[1]
			],
			boundary_right_bottom=[
				x2,
				y2 if self.height is not None else self.render_boundary_right_bottom[1]
			],

			parent_width=x2 - x1,
			parent_height=y2 - y1,

			stretch=self.render_stretch
		)