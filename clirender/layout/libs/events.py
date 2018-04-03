from library import Library
from ..patch import patch
from ..nodes import Node, Generator

class Events(Library):
	@patch(Node, Generator)
	class Node(object):
		def __init__(self, **kwargs):
			patch.super(self).__init__(**kwargs)

			self._events = {}

		def on(self, event, handler):
			if event not in self._events:
				self._events[event] = []

			self._events[event].append(handler)

		def emit(self, event, *args, **kwargs):
			for handler in self._events.get(event, []):
				handler(*args, **kwargs)