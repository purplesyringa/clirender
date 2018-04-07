from node import Node

class Container(Node):
	container = True
	text_container = False
	properties = []

	def onRender(self, dry_run=False):
		if len(self.children) != 1:
			raise ValueError("<Container> can contain only one node")

		return self.renderChild(
			self.children[0], dry_run=dry_run,

			offset=self.render_offset,
			boundary_left_top=self.render_boundary_left_top,
			boundary_right_bottom=self.render_boundary_right_bottom,
			parent_width=self.render_parent_width,
			parent_height=self.render_parent_height,
			stretch=self.render_stretch,

			completely_revoked=self._completely_revoked
		)