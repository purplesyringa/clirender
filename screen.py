import sys
import size

from colorama import Fore, Back, Style

import colorama
colorama.init()

class Screen(object):
	class Resized(Exception):
		pass

	def __init__(self):
		self.terminal_size = self.getTerminalSize()

	def loop(self, handler):
		while True:
			cur = self.getTerminalSize()
			if self.terminal_size != cur:
				raise Screen.Resized
			self.terminal_size = cur

			handler(self)

	def getTerminalSize(self):
		return size.get_terminal_size()

	def write(self, data):
		sys.stdout.write(data)


	def clear(self):
		self.write("\033[2J\033[1;1f")

	def moveCursor(self, x, y):
		self.write("\x1b[%d;%dH" % (y + 1, x + 1))

	def printAt(self, text, x, y):
		self.moveCursor(x, y)
		self.write(text)

	def colorize(self, text, fg=None, bg=None, bright=False):
		if fg is not None:
			text = getattr(Fore, fg.upper()) + text
		if bg is not None:
			text = getattr(Back, bg.upper()) + text
		if bright:
			text = Style.BRIGHT + text

		text += Style.RESET_ALL
		return text