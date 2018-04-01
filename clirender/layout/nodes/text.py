from node import Node

class Text(Node):
	container = False
	text_container = True

	def __init__(self, value, width=None, bg=None, color=None, bright=False, fill=False):
		super(Text, self).__init__(value=value)

		self.width = width
		self.bg = bg
		self.color = color
		self.bright = bright is not False
		self.fill = fill is not False

	def render(self, dry_run=False):
		if self.width is not None:
			width = self.width
			width = self.layout.calcRelativeSize(width, self.render_boundary_right_bottom[0] - self.render_boundary_left_top[0], self.render_stretch)
		else:
			width = len(self.value)

		x1, y1 = map(max, zip(self.render_offset, self.render_boundary_left_top))

		x2, y2 = self.render_offset[0] + width, self.render_offset[1] + 1
		x2, y2 = map(min, zip((x2, y2), self.render_boundary_right_bottom))

		bg = self.inherit("bg")
		color = self.inherit("color")
		bright = self.inherit("bright")

		if color is not None:
			if not dry_run:
				if self.fill:
					self.layout.screen.fill(x1, y1, x2, y2, char=self.value, style=lambda s: self.layout.screen.colorize(s, bg=bg, fg=color, bright=bright))
				else:
					self.layout.screen.printAt(self.layout.screen.colorize(self.value, bg=bg, fg=color, bright=self.bright), x1, y1)
					self.layout.screen.printAt(self.layout.screen.colorize(" " * int(width - len(self.value)), bg=bg), x1 + len(self.value), y1)

		return x1, y1, x2, y2