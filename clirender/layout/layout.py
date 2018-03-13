from __future__ import division

import numbers
import re
import numexpr
from clirender.screen import Screen
from exceptions import NoStretchError

class Layout(object):
	def __init__(self, root):
		self.screen = Screen()
		self.root = root

	def render(self):
		self.screen.clear()

		self.root.render_offset = (0, 0)
		self.root.render_boundary_left_top = [0, 0]
		self.root.render_boundary_right_bottom = list(self.screen.terminal_size)
		self.root.parent = None
		self.root.render_stretch = self.screen.terminal_size[0]

		self.root.render(self)

	def calcRelativeSize(self, size, total, stretch=None, expression=True):
		if not expression:
			# Maybe just absolute integer or float?
			try:
				return float(size)
			except ValueError:
				pass

			# Percent?
			try:
				if size.endswith("%"):
					return float(size[:-1]) / 100 * total
			except ValueError:
				pass

			raise ValueError("Cannot parse %s as non-expression offset/size" % size)

		if not isinstance(size, str) and not isinstance(size, unicode):
			return self.calcRelativeSize(size, total, stretch=stretch, expression=False)


		if stretch is not None:
			stretch = self.calcRelativeSize(stretch, total)


		# Replace percents
		size = re.sub(r"\b([\d\.]+%)(?=\s|$)", lambda x: str(self.calcRelativeSize(x.group(1), total, stretch=stretch, expression=False)), size)

		try:
			data = {}
			if stretch is not None:
				data["stretch"] = stretch

			return numexpr.evaluate(size, local_dict={}, global_dict=data).item()
		except KeyError as e:
			if e.args[0] == "stretch":
				raise NoStretchError()