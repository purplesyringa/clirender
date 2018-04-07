from library import Library
from ..nodes import Generator, Node
from ..api import NodeAPI
from ..patch import patch
import operator

class Scrollable(Library):
	class Scrolled(Node):
		container = True
		text_container = False
		properties = ["x", "y"]

		def init(self, x=0, y=0):
			self.x = float(x)
			self.y = float(y)

		def onRender(self, dry_run=False):
			if len(self.children) != 1:
				raise ValueError("<Scrolled> can contain only one node")

			offset = list(self.render_offset)
			offset = map(operator.sub, offset, (self.x, self.y))
			offset = tuple(offset)

			rendered = self.renderChild(
				self.children[0], dry_run=dry_run,

				offset=offset,
				plus_size=(self.x, self.y),
				boundary_left_top=self.render_boundary_left_top,
				boundary_right_bottom=self.render_boundary_right_bottom,
				parent_width=self.render_parent_width,
				parent_height=self.render_parent_height,
				stretch=self.render_stretch,

				completely_revoked=self._completely_revoked
			)

			return map(operator.sub, rendered, (self.x, self.y))

	@patch(NodeAPI)
	class NodeAPI(object):
		def scrollIntoView(self, coords=["x", "y"]):
			try:
				if not self.isNode():
					raise self._unexpectedType("scrollIntoView()")

				boundaryBox = self.getBoundaryBox()

				root = self.nearest(lambda node: node.nodeName == "Scrolled")
				rootBoundaryBox = root.getBoundaryBox()

				# Thanks to https://github.com/litera/jquery-scrollintoview/blob/master/jquery.scrollintoview.js
				rel = dict(
					top=boundaryBox["top"] - rootBoundaryBox["top"],
					bottom=rootBoundaryBox["bottom"] - boundaryBox["bottom"],
					left=boundaryBox["left"] - rootBoundaryBox["left"],
					right=rootBoundaryBox["right"] - boundaryBox["right"]
				)

				if "y" in coords:
					if rel["top"] < 0:
						root["y"] += rel["top"]
					elif rel["top"] > 0 and rel["bottom"] < 0:
						root["y"] += min(rel["top"], -rel["bottom"])
				if "x" in coords:
					if rel["left"] < 0:
						root["x"] += rel["left"]
					elif rel["left"] > 0 and rel["right"] < 0:
						root["x"] += min(rel["left"], -rel["right"])
			except Exception, e:
				print e