import sys

import size

class Screen(object):
	class Resized(Exception):
		pass

	class Ansi(object):
		class Colors(object):
			black = 0
			red = 1
			green = 2
			yellow = 3
			blue = 4
			magenta = 5
			cyan = 6
			white = 7

			def bright(self, color):
				return color + 60

			def fg(self, color):
				return Ansi.csi() + str(color + 30) + "m"
			def bg(self, color):
				return Ansi.csi() + str(color + 40) + "m"

			def reset(self):
				return Ansi.csi() + "0m"

		@staticmethod
		def esc(self):
			return chr(27)

		@staticmethod
		def csi(self):
			return self.esc() + "["

		@staticmethod
		def up(self, cnt):
			return self.csi() + str(cnt) + "A"
		@staticmethod
		def down(self, cnt):
			return self.csi() + str(cnt) + "B"
		@staticmethod
		def right(self, cnt):
			return self.csi() + str(cnt) + "C"
		@staticmethod
		def left(self, cnt):
			return self.csi() + str(cnt) + "D"

		@staticmethod
		def move(self, x, y=None):
			if y is not None:
				return self.csi() + str(y + 1) + ";" + str(x + 1) + "H"
			else:
				return self.csi() + str(x + 1) + "G"

		@staticmethod
		def clear(self):
			return self.csi() + "3J"

	def __init__(self, handler):
		self.terminal_size = (0, 0)

		while True:
			cur = self.getTerminalSize()
			if self.terminal_size != (0, 0) and self.terminal_size != cur:
				raise Screen.Resized
			self.terminal_size = cur

			handler(self)

	def getTerminalSize(self):
		return size.get_terminal_size()

	def write(self, data):
		sys.stdout.write(data)