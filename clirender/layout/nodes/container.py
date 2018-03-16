from node import Node

class Container(Node):
	container = True
	text_container = False

	def __init__(self, children=[]):
		super(Container, self).__init__(children=children)

		self.type = None

	def render(self, layout, dry_run=False):
		if len(self.getChildren()) != 1:
			raise ValueError("<Container> can contain only one node")

		child = self.getChildren()[0]

		child.render_offset = self.render_offset
		child.render_boundary_left_top = self.render_boundary_left_top
		child.render_boundary_right_bottom = self.render_boundary_right_bottom
		child.render_stretch = self.render_stretch
		child.parent = self

		return child.render(layout, dry_run=dry_run)