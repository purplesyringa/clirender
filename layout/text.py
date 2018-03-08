from node import Node

class Text(Node):
	container = False
	text_container = True

	def __init__(self, value, width=None, bg=None, color=None, bright=False, fill=False):
		super(Text, self).__init__()

		self.value = value
		self.width = width
		self.bg = bg
		self.color = color
		self.bright = bright is not False
		self.fill = fill is not False

	def render(self, layout, dry_run=False):
		if self.width is not None:
			width = self.width
			width = layout.calcRelativeSize(width, self.render_boundary_right_bottom[0] - self.render_boundary_left_top[0])
		else:
			width = len(self.value)

		x1, y1 = map(max, zip(self.render_offset, self.render_boundary_left_top))

		x2, y2 = self.render_offset[0] + width, self.render_offset[1] + 1
		x2, y2 = map(min, zip((x2, y2), self.render_boundary_right_bottom))

		if self.color is not None:
			if not dry_run:
				if self.fill:
					layout.screen.fill(x1, y1, x2, y2, char=self.value, style=lambda s: layout.screen.colorize(s, bg=self.bg, fg=self.color, bright=self.bright))
				else:
					layout.screen.printAt(layout.screen.colorize(self.value, bg=self.bg, fg=self.color, bright=self.bright), x1, y1)
					layout.screen.printAt(layout.screen.colorize(" " * int(width - len(self.value)), bg=self.bg), x1 + len(self.value), y1)

		return x1, y1, x2, y2