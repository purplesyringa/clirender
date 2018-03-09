from node import Node

class Container(Node):
	container = True
	text_container = False

	def __init__(self, children=[]):
		super(Container, self).__init__()

		if len(children) != 1:
			raise ValueError("<Container> can contain only one node")

		self.child = children[0]

	def render(self, layout, dry_run=False):
		self.child.render_offset = self.render_offset
		self.child.render_boundary_left_top = self.render_boundary_left_top
		self.child.render_boundary_right_bottom = self.render_boundary_right_bottom

		return self.child.render(layout, dry_run=dry_run)