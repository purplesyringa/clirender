from screen import Screen

class Layout(object):
	def __init__(self, root):
		self.screen = Screen()
		self.root = root

	def render(self):
		self.screen.clear()

		self.root.render_offset = (0, 0)
		self.root.render_boundary_left_top = (0, 0)
		self.root.render_boundary_right_bottom = self.screen.terminal_size

		self.root.render(self)