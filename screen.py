import sys
import size

from colorama import Fore, Back as Background, Style

import colorama
colorama.init()

class Screen(object):
	class Resized(Exception):
		pass

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


	def moveCursor(self, x, y):
		self.write("\x1b[%d;%dH" % (y, x))

	def printAt(self, text, x, y):
		self.moveCursor(x, y)
		self.write(text)