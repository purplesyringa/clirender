from library import Library
from ..patch import patch
from ..nodes import Node, Generator
from ..api import createAPI

class Events(Library):
	@patch(Node, Generator)
	class Node(object):
		def __init__(self, **kwargs):
			self._events = {}

			for name, handler in kwargs.items():
				if name.startswith("on") and name != "on":
					event = name[2].lower() + name[3:]
					if not callable(handler):
						raise ValueError("Non-callable %s handler was passed to %s: %s" % (name, self, handler))

					del kwargs[name]

					handler = Events.safe(handler, self)

					self.on(event, handler)

			patch.super(self).__init__(**kwargs)

		def on(self, event, handler):
			if event not in self._events:
				self._events[event] = []

			self._events[event].append(handler)

		def emit(self, event, *args, **kwargs):
			for handler in self._events.get(event, []):
				handler(*args, **kwargs)

	@staticmethod
	def safe(handler, node):
		def wrapper(*args, **kwargs):
			return handler(self=createAPI(node), *args, **kwargs)
		return wrapper