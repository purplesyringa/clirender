import sys, platform
import size

from colorama import Fore, Back, Style

import colorama

class Screen(object):
	class Resized(Exception):
		pass

	def __init__(self):
		if platform.system().lower() == "windows":
			build = int(platform.win32_ver()[1].split(".")[-1])
			if build < 10525:
				# Before build 10525, ANSI escapes were not handled by Windows
				self.color_support = "simulation"

				# Colorama will simulate some ANSI escapes with WinAPI calls
				colorama.init()
			elif build < 16257:
				# Before build 16257, ANSI escapes were enabled by default
				self.color_support = "full"
			elif build >= 16257:
				# As of build 16257, we need to enable ANSI escapes manually
				self.color_support = "full"

				from ctypes import windll, c_int, byref
				stdout_handle = windll.kernel32.GetStdHandle(c_int(-11))
				mode = c_int(0)
				windll.kernel32.GetConsoleMode(c_int(stdout_handle), byref(mode))
				mode = c_int(mode.value | 4)
				windll.kernel32.SetConsoleMode(c_int(stdout_handle), mode)
		else:
			# On Linux and Darwin, ANSI escapes just work.
			self.color_support = "full"

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
		self.moveCursor(int(x), int(y))
		self.write(text)

	def decodeColor(self, color, foreground):
		if "|" in color:
			color, fallback = color.split("|", 1)
		else:
			fallback = None

		color = color.strip()

		if color.lower() in ["black", "blue", "cyan", "green", "magenta", "red", "white", "yellow"]:
			# Colorama supports these names of colors
			return getattr(Fore if foreground else Back, color.upper())
		elif color.startswith("#"):
			# Hex color
			color = color[1:]

			if len(color) == 3:
				# #ABC = #AABBCC
				color = color[0] * 2 + color[1] * 2 + color[2] * 2

			if len(color) != 6:
				raise ValueError("Invalid %s color #%s" % ("foreground" if foreground else "background", color))

			if self.color_support != "full":
				if fallback is not None:
					return self.decodeColor(fallback, foreground)
				raise ValueError("24-bit colors don't work on this platform")

			r, g, b = color[:2], color[2:4], color[4:]
			r, g, b = int(r, 16), int(g, 16), int(b, 16)

			return "\x1B[%s;2;%s;%s;%sm" % (38 if foreground else 48, r, g, b)
		else:
			raise ValueError("Unknown %s color %s" % ("foreground" if foreground else "background", color))

	def colorize(self, text, fg=None, bg=None, bright=False):
		if fg is not None:
			text = self.decodeColor(fg, True) + text
		if bg is not None:
			text = self.decodeColor(bg, False) + text
		if bright:
			text = Style.BRIGHT + text

		text += Style.RESET_ALL
		return text

	def fill(self, x1, y1, x2, y2, char=" ", style=lambda s: s):
		s = char * (int(x2) - int(x1))
		for y in range(int(y1), int(y2)):
			self.printAt(style(s), x=int(x1), y=y)