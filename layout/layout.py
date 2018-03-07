from __future__ import division

import numbers
from screen import Screen

class Layout(object):
	def __init__(self, root):
		self.screen = Screen()
		self.root = root

	def render(self):
		self.screen.clear()

		self.root.render_offset = (0, 0)
		self.root.render_boundary_left_top = (0, 0)
		self.root.render_boundary_right_bottom = self.screen.terminal_size

		self.root.render(self)

	def calcRelativeSize(self, size, total):
		# Maybe just absolute integer?
		if isinstance(size, numbers.Integral):
			return size

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

		raise ValueError("Cannot parse %s as offset/size literal" % size)