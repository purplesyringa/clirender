from node import Node

class Text(Node):
	container = False
	text_container = True
	properties = ["width", "bg", "color", "bright", "fill", "wrap"]

	def init(self, width=None, height=None, bg=None, color=None, bright=False, fill=False, wrap=False):
		self.width = width
		self.height = height
		self.bg = bg
		self.color = color
		self.bright = bright is not False
		self.fill = fill is not False
		self.wrap = wrap is not False

	def onRender(self, dry_run=False):
		if self.wrap:
			if self.width is not None:
				width = self.width
				width = self.layout.calcRelativeSize(width, self.render_parent_width, self.render_stretch)
			else:
				width = max(self.render_boundary_right_bottom[0] - self.render_offset[0], 0)

			if int(width) == 0:
				lines = []
			else:
				import textwrap
				lines = textwrap.wrap(self.value, width=int(width))
		else:
			lines = self.value.split("\n")

		if lines == []:
			lines = [""]

		if self.width is not None:
			width = self.width
			width = self.layout.calcRelativeSize(width, self.render_parent_width, self.render_stretch)
		else:
			width = max(len(line) for line in lines)

		if self.height is not None:
			height = self.height
			height = self.layout.calcRelativeSize(height, self.render_parent_height, self.render_stretch)
		else:
			height = len(lines)

		width += self.render_plus_size[0]
		height += self.render_plus_size[1]

		x, y = self.render_offset


		lines = [line[:int(width)] for line in lines]
		cwidth, cheight = width, height

		# Left boundary
		pos = max(self.render_boundary_left_top[0] - x, 0)
		lines = [line[int(pos):] for line in lines]
		x = max(x, self.render_boundary_left_top[0])

		# Right boundary
		pos = max(x + cwidth - self.render_boundary_right_bottom[0], 0)
		if pos > 0:
			lines = [line[:cwidth-int(pos)] for line in lines]
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
					for i, line in enumerate(lines):
						self.layout.screen.printAt(self.layout.screen.colorize(line, bg=bg, fg=color, bright=self.bright), x, y + i)
						self.layout.screen.printAt(self.layout.screen.colorize(" " * int(cwidth - len(line)), bg=bg), x + len(line), y + i)

		return width, height