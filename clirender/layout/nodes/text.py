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


		text = self.value[:int(width)]
		cwidth, cheight = width, height

		# Left boundary
		text = text[int(max(self.render_boundary_left_top[0] - x, 0)):]
		x = max(x, self.render_boundary_left_top[0])

		# Right boundary
		pos = max(x + cwidth - self.render_boundary_right_bottom[0], 0)
		if pos > 0:
			text = text[:-int(pos)]
		cwidth = min(cwidth, self.render_boundary_right_bottom[0] - x)

		# Top boundary
		if self.fill:
			y = max(y, self.render_boundary_left_top[1])

		# Bottom boundary
		cheight = min(cheight, self.render_boundary_right_bottom[1] - y)


		if x < self.render_boundary_left_top[0] or x >= self.render_boundary_right_bottom[0]:
			return width, height
		elif y < self.render_boundary_left_top[1] or y >= self.render_boundary_right_bottom[1]:
			return width, height
		elif cwidth == 0 or cheight == 0:
			return width, height

		bg = self.inherit("bg")
		color = self.inherit("color")
		bright = self.inherit("bright")

		if color is not None:
			if not dry_run:
				if self.fill:
					self.layout.screen.fill(x, y, x + cwidth, y + cheight, char=self.value, style=lambda s: self.layout.screen.colorize(s, bg=bg, fg=color, bright=bright))
				else:
					self.layout.screen.printAt(self.layout.screen.colorize(text, bg=bg, fg=color, bright=self.bright), x, y)
					self.layout.screen.printAt(self.layout.screen.colorize(" " * int(cwidth - len(text)), bg=bg), x + len(text), y)

		return width, height