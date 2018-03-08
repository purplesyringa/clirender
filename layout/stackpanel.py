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

		cur_x, cur_y = x1, y1

		for child in self.children:
			child.render_offset = (cur_x, cur_y)
			child.render_boundary_left_top = [x1, y1]
			child.render_boundary_right_bottom = [x2, y2]

			child_x1, child_y1, child_x2, child_y2 = child.render(layout, dry_run=dry_run)

			if self.vertical:
				cur_y = child_y2
			else:
				cur_x = child_x2

		return x1, y1, x2, y2

	def guessContainerSize(self, layout):
		x1, y1, _, _ = super(StackPanel, self).render(layout, dry_run=True, width=0, height=0)

		cur_x, cur_y = x1, y1
		max_width, max_height = 0, 0

		for child in self.children:
			child.render_offset = (cur_x, cur_y)
			child.render_boundary_left_top = [0, 0]
			child.render_boundary_right_bottom = list(layout.screen.terminal_size)

			child_x1, child_y1, child_x2, child_y2 = child.render(layout, dry_run=True)

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