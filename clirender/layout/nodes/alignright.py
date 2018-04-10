from rect import Rect

class AlignRight(Rect):
	container = True
	text_container = False
	properties = ["width", "height", "bg"]

	def init(self, **kwargs):
		if "height" not in kwargs:
			kwargs["height"] = None
		return kwargs

	def onRender(self, dry_run=False):
		if len(self.children) != 1:
			raise ValueError("<AlignRight> can contain only one node")

		# Get child size
		child_width, child_height = self.guessContainerSize()

		# Guess container size
		if self.height is None:
			height = child_height
		else:
			height = self.height

		width, height = self.render(AlignRight, dry_run=dry_run, height=height)
		self.renderChildren(width, height, dry_run=dry_run, child_width=child_width)

		return width, height

	def guessContainerSize(self):
		width, height = self.render(AlignRight, dry_run=True, width=self.width, height=self.height or 0)
		return self.renderChildren(width, height, dry_run=True)

	def renderChildren(self, width, height, dry_run=False, child_width=None):
		x1, y1 = self.render_offset
		x2, y2 = x1 + width, y1 + height

		if child_width is not None:
			x1 = x2 - child_width

		child = self.children[0]
		return self.renderChild(
			child, dry_run=dry_run,

			offset=(x1, y1),

			boundary_left_top=map(max, [
				x1,
				y1 if self.height is not None else self.render_boundary_left_top[1]
			], self.render_boundary_left_top),
			boundary_right_bottom=map(min, [
				x2,
				y2 if self.height is not None else self.render_boundary_right_bottom[1]
			], self.render_boundary_right_bottom),

			parent_width=width,
			parent_height=height,

			stretch=self.render_stretch
		)