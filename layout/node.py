class Node(object):
	container = False
	text_container = False

	def __init__(self):
		self.render_offset = (None, None)
		self.render_boundary_left_top = (None, None)
		self.render_boundary_right_bottom = (None, None)

		self.render_children = []

	def render(self, layout):
		raise NotImplementedError