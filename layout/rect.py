class Rect(object):
	def __init__(self, width=None, height=None, bg=None):
		self.width = width
		self.height = height
		self.bg = bg

		self.render_offset = (None, None)
		self.render_boundary_left_top = (None, None)
		self.render_boundary_right_bottom = (None, None)

	def render(self, layout):
		x1, y1 = map(lambda x: min(*x), zip(self.render_offset, self.render_boundary_left_top))

		x2, y2 = self.render_offset[0] + self.width, self.render_offset[1] + self.height
		x2, y2 = map(lambda x: min(*x), zip((x2, y2), self.render_boundary_right_bottom))

		layout.screen.fill(x1, y1, x2, y2, char=" ", style=lambda s: layout.screen.colorize(s, bg=self.bg))