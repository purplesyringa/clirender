from node import Node

class Switch(Node):
	container = False
	text_container = False

	def __init__(self):
		super(Switch, self).__init__()

	def render(self, layout, dry_run=False):
		x1, y1 = map(max, zip(self.render_offset, self.render_boundary_left_top))
		return x1, y1, x1, y1