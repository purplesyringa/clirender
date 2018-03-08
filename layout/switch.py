from node import Node

class Switch(Node):
	container = False
	text_container = False

	def __init__(self):
		super(Switch, self).__init__()

	def render(self, layout, dry_run=False):
		raise ValueError("<Switch> must be used inside <StackPanel> only")