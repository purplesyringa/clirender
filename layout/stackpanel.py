from rect import Rect
import random

class StackPanel(Rect):
	def __init__(self, width=None, height=None, bg=None, vertical=False, children=[]):
		super(StackPanel, self).__init__(width=width, height=height, bg=bg)

		self.vertical = vertical
		self.children = children

	def render(self, layout):
		x1, y1, x2, y2 = super(StackPanel, self).render(layout)

		cur_x, cur_y = x1, y1

		for child in self.children:
			child.render_offset = (cur_x, cur_y)
			child.render_boundary_left_top = (x1, y1)
			child.render_boundary_right_bottom = (x2, y2)

			child_x1, child_y1, child_x2, child_y2 = child.render(layout)

			if self.vertical:
				cur_y = child_y2
			else:
				cur_x = child_x2

		return x1, y1, x2, y2