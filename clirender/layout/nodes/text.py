from node import Node

class Text(Node):
	container = False
	text_container = True
	properties = ["width", "bg", "color", "bright", "fill"]

	def init(self, width=None, height=None, bg=None, color=None, bright=False, fill=False):
		self.width = width
		self.height = height
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

		if self.height is not None:
			height = self.height
			height = self.layout.calcRelativeSize(height, self.render_parent_height, self.render_stretch)
		else:
			height = 1

		width += self.render_plus_size[0]
		height += self.render_plus_size[1]

		x, y = self.render_offset

		if not (self.render_boundary_left_top[0] <= x <= x + width <= self.render_boundary_right_bottom[0]):
			return width, height
		elif not (self.render_boundary_left_top[1] <= y <= y + height <= self.render_boundary_right_bottom[1]):
			return width, height

		bg = self.inherit("bg")
		color = self.inherit("color")
		bright = self.inherit("bright")

		if color is not None:
			if not dry_run:
				if self.fill:
					self.layout.screen.fill(x, y, x + width, y + height, char=self.value, style=lambda s: self.layout.screen.colorize(s, bg=bg, fg=color, bright=bright))
				else:
					self.layout.screen.printAt(self.layout.screen.colorize(self.value, bg=bg, fg=color, bright=self.bright), x, y)
					self.layout.screen.printAt(self.layout.screen.colorize(" " * int(width - len(self.value)), bg=bg), x + len(self.value), y)

		return width, height