from library import Library
from ..nodes import Generator, Node
import operator

class Scrollable(Library):
	class Scrolled(Node):
		container = True
		text_container = False
		properties = ["x", "y"]

		def __init__(self, x=0, y=0, children=[]):
			super(Scrollable.Scrolled, self).__init__(children=children)
			self.x = float(x)
			self.y = float(y)

		def render(self, dry_run=False):
			if len(self.children) != 1:
				raise ValueError("<Scrolled> can contain only one node")

			offset = list(self.render_offset)
			offset = map(operator.sub, offset, (self.x, self.y))
			offset = tuple(offset)

			return self.renderChild(
				self.children[0], dry_run=dry_run,

				offset=offset,
				plus_size=(self.x, self.y),
				boundary_left_top=self.render_boundary_left_top,
				boundary_right_bottom=self.render_boundary_right_bottom,
				parent_width=self.render_parent_width,
				parent_height=self.render_parent_height,
				stretch=self.render_stretch
			)