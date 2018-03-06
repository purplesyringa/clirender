from screen import Screen


def init(screen):
	screen.clear()

def loop(screen):
	try:
		screen.printAt("Hello", 2, 2)
	except IOError:
		pass

Screen(loop, init=init)