from node import Node

class Rect(Node):
	container = False
	text_container = False

	def __init__(self, width, height, bg=None):
		super(Rect, self).__init__()

		self.width = width
		self.height = height
		self.bg = bg

	def render(self, layout, dry_run=False, width=None, height=None):
		if width is None:
			width = self.width
		if height is None:
			height = self.height

		width  = layout.calcRelativeSize(width,  self.render_boundary_right_bottom[0] - self.render_boundary_left_top[0])
		height = layout.calcRelativeSize(height, self.render_boundary_right_bottom[1] - self.render_boundary_left_top[1])

		x1, y1 = map(max, zip(self.render_offset, self.render_boundary_left_top))

		x2, y2 = self.render_offset[0] + width, self.render_offset[1] + height
		x2, y2 = map(min, zip((x2, y2), self.render_boundary_right_bottom))

		if self.bg is not None:
			if not dry_run:
				layout.screen.fill(x1, y1, x2, y2, char=" ", style=lambda s: layout.screen.colorize(s, bg=self.bg))

		return x1, y1, x2, y2