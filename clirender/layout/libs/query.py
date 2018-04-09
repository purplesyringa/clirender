from library import Library
from ..nodes import Element
from ..patch import patch
from ..api import LayoutAPI, createAPI
from ..layout import Layout

class Query(Library):
	@patch(Layout)
	class Layout(object):
		def __init__(self, *args, **kwargs):
			patch.super(Query.Layout, self).__init__(*args, **kwargs)
			self._byTagName = {}

	@patch(Element)
	class Element(object):
		def init(self, **kwargs):
			tag = type(self).__name__
			if tag not in self.layout._byTagName:
				self.layout._byTagName[tag] = []
			self.layout._byTagName[tag].append(self)

			patch.super(Query.Element, self).init(**kwargs)

		def destroy(self):
			tag = type(self).__name__
			self.layout._byTagName[tag].remove(self)

			patch.super(Query.Element, self).destroy()

	@patch(LayoutAPI)
	class LayoutAPI(object):
		def byTagName(self, name):
			return [createAPI(node) for node in self._byTagName.get(name, [])]