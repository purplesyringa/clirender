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

		return self.renderChild(
			layout, self.getChildren()[0], dry_run=dry_run,

			offset=self.render_offset,
			boundary_left_top=self.render_boundary_left_top,
			boundary_right_bottom=self.render_boundary_right_bottom,
			stretch=self.render_stretch
		)