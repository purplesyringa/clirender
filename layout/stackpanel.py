from rect import Rect

class StackPanel(Rect):
	container = True
	text_container = False

	def __init__(self, width=None, height=None, bg=None, orientation="horizontal", children=[]):
		super(StackPanel, self).__init__(width=width, height=height, bg=bg)

		self.vertical = orientation.lower() == "vertical"
		self.children = children

	def render(self, layout, dry_run=False):
		# Guess container size
		if self.width is None or self.height is None:
			width, height = self.guessContainerSize(layout)
			if self.width is not None:
				width = self.width
			if self.height is not None:
				height = self.height
		else:
			# If the size is given, don't do unnecessary actions
			width, height = self.width, self.height

		x1, y1, x2, y2 = super(StackPanel, self).render(layout, dry_run=dry_run, width=width, height=height)
		self.renderChildren(layout, x1, y1, x2, y2, dry_run=dry_run)

		return x1, y1, x2, y2

	def guessContainerSize(self, layout):
		x1, y1, x2, y2 = super(StackPanel, self).render(layout, dry_run=True, width=self.width or 0, height=self.height or 0)

		return self.renderChildren(layout, x1, y1, x2, y2, dry_run=True)

	def renderChildren(self, layout, x1, y1, x2, y2, dry_run=False):
		cur_x, cur_y = x1, y1
		max_width, max_height = 0, 0

		for child in self.children:
			child.render_offset = (cur_x, cur_y)

			child.render_boundary_left_top = self.render_boundary_left_top
			child.render_boundary_right_bottom = self.render_boundary_right_bottom

			if self.width is not None:
				child.render_boundary_left_top[0] = x1
				child.render_boundary_right_bottom[0] = x2
			if self.height is not None:
				child.render_boundary_left_top[1] = y1
				child.render_boundary_right_bottom[1] = y2

			child_x1, child_y1, child_x2, child_y2 = child.render(layout, dry_run=dry_run)

			max_width = max(max_width, child_x2 - child_x1)
			max_height = max(max_height, child_y2 - child_y1)

			if self.vertical:
				cur_y = child_y2
			else:
				cur_x = child_x2

		if self.vertical:
			return max_width, cur_y - y1
		else:
			return cur_x - x1, max_height