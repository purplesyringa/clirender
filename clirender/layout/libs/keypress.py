from library import Library
import os

def waitKey():
	result = None
	if os.name == "nt":
		import msvcrt
		result = msvcrt.getch()
	else:
		import termios
		fd = sys.stdin.fileno()

		oldterm = termios.tcgetattr(fd)
		newattr = termios.tcgetattr(fd)
		newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
		termios.tcsetattr(fd, termios.TCSANOW, newattr)

		try:
			result = sys.stdin.read(1)
		except IOError:
			pass
		finally:
			termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)

	return result

class KeyPress(Library):
	def beforeLoop(self, instances):
		self.key = None
		self.instances = instances

	def loop(self, instances):
		if self.key is None:
			self.key = ord(waitKey())
		if self.key == 3:
			raise KeyboardInterrupt

	def getKey(self):
		if self.key is None:
			self.loop(self.instances)
		return self.key