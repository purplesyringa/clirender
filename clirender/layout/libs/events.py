from library import Library
from ..patch import patch
from ..nodes import Element
from ..api import createAPI

class Events(Library):
	@patch(Element)
	class Element(object):
		def init(self, **kwargs):
			self._events = {}

			for name, handler in kwargs.items():
				if name.startswith("on") and name != "on":
					event = name[2].lower() + name[3:]
					if not callable(handler):
						raise ValueError("Non-callable %s handler was passed to %s: %s" % (name, self, handler))

					del kwargs[name]

					handler = Events.safe(handler, self)

					self.on(event, handler)

			patch.super(Events.Element, self).init(**kwargs)


		def on(self, event, handler):
			if event not in self._events:
				self._events[event] = []

			self._events[event].append(handler)

		def emit(self, event, *args, **kwargs):
			if "recursive" in kwargs:
				recursive = kwargs["recursive"]
				del kwargs["recursive"]
			else:
				recursive = False

			for handler in self._events.get(event, []):
				handler(*args, **kwargs)

			if recursive and self.gen_parent:
				self.gen_parent.emit(event, recursive=True, *args, **kwargs)

	@staticmethod
	def safe(handler, node):
		def wrapper(*args, **kwargs):
			return handler(self=createAPI(node), *args, **kwargs)
		return wrapper