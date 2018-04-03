from library import Library, patch
from ..nodes import Node

class Events(Library):
	@patch(Node)
	class Node(object):
		def __init__(self, *args, **kwargs):
			super(Events.Node, self).__init__(*args, **kwargs)

			self._events = {}

		def on(self, event, handler):
			if event not in self._events:
				self._events[event] = []

			self._events[event].append(handler)

		def emit(self, event, *args, **kwargs):
			for handler in self._events.get(event, []):
				handler(*args, **kwargs)