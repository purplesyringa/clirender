from __future__ import division

import numbers
import re
import numexpr
from screen import Screen
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

	def calcRelativeSize(self, size, total, stretch=None):
		if stretch is not None:
			stretch = self.calcRelativeSize(stretch, total)

		# Maybe just absolute integer or float?
		try:
			return float(size)
		except ValueError:
			pass

		# If it isn't a string, what can it be?
		if not isinstance(size, str) and not isinstance(size, unicode):
			raise ValueError("Offset/size is %s, not int or str" % type(size))

		# Maybe this is a str(int) ?
		try:
			return int(size)
		except ValueError:
			pass

		# Percent?
		try:
			if size.endswith("%"):
				return float(size[:-1]) / 100 * total
		except ValueError:
			pass

		# Calculations?
		if size.startswith("="):
			expression = size[1:]

			# Replace percents
			expression = re.sub(r"\b([\d\.]+%)(?=\s|$)", lambda x: str(self.calcRelativeSize(x.group(1), total, stretch=stretch)), expression)

			try:
				data = {}
				if stretch is not None:
					data["stretch"] = stretch

				return numexpr.evaluate(expression, local_dict={}, global_dict=data).item()
			except KeyError as e:
				if e.args[0] == "stretch":
					raise NoStretchError()

				raise

		raise ValueError("Cannot parse %s as offset/size literal" % size)