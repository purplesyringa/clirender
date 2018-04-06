from node import Node

class Switch(Node):
	container = False
	text_container = False
	properties = []

	def __init__(self, **kwargs):
		super(Switch, self).__init__(**kwargs)

	def render(self, dry_run=False):
		raise ValueError("<Switch> must be used inside <StackPanel> only")