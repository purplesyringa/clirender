from node import Node

class Rect(Node):
	container = False
	text_container = False
	properties = ["width", "height", "bg"]

	def init(self, width, height, bg=None):
		self.width = width
		self.height = height
		self.bg = bg

	def onRender(self, dry_run=False, width=None, height=None):
		if width is None:
			width = self.width
		if height is None:
			height = self.height

		width  = self.layout.calcRelativeSize(width,  self.render_parent_width , self.render_stretch) + self.render_plus_size[0]
		height = self.layout.calcRelativeSize(height, self.render_parent_height, self.render_stretch) + self.render_plus_size[1]

		x1, y1 = map(max, zip(self.render_offset, self.render_boundary_left_top))

		x2, y2 = self.render_offset[0] + width, self.render_offset[1] + height
		x2, y2 = map(min, zip((x2, y2), self.render_boundary_right_bottom))

		bg = self.inherit("bg")

		if bg is not None:
			if not dry_run:
				self.layout.screen.fill(x1, y1, x2, y2, char=" ", style=lambda s: self.layout.screen.colorize(s, bg=bg))

		return width, height