from node import Node

class Text(Node):
	container = False
	text_container = True
	properties = ["width", "bg", "color", "bright", "fill"]

	def init(self, width=None, bg=None, color=None, bright=False, fill=False):
		self.width = width
		self.bg = bg
		self.color = color
		self.bright = bright is not False
		self.fill = fill is not False

	def onRender(self, dry_run=False):
		if self.width is not None:
			width = self.width
			width = self.layout.calcRelativeSize(width, self.render_parent_width, self.render_stretch)
		else:
			width = len(self.value)

		width += self.render_plus_size[0]

		x, y = self.render_offset

		if not (self.render_boundary_left_top[0] <= x <= x + width <= self.render_boundary_right_bottom[0]):
			return width, 1
		elif not (self.render_boundary_left_top[1] <= y < self.render_boundary_right_bottom[1]):
			return width, 1

		bg = self.inherit("bg")
		color = self.inherit("color")
		bright = self.inherit("bright")

		if color is not None:
			if not dry_run:
				if self.fill:
					self.layout.screen.fill(x, y, x + width, y + 1, char=self.value, style=lambda s: self.layout.screen.colorize(s, bg=bg, fg=color, bright=bright))
				else:
					self.layout.screen.printAt(self.layout.screen.colorize(self.value, bg=bg, fg=color, bright=self.bright), x, y)
					self.layout.screen.printAt(self.layout.screen.colorize(" " * int(width - len(self.value)), bg=bg), x + len(self.value), y)

		return width, 1