from node import Node

class Switch(Node):
	container = False
	text_container = False
	properties = []

	def onRender(self, dry_run=False):
		raise ValueError("<Switch> must be used inside <StackPanel> only")