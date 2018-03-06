from screen import Screen

def loop(screen):
	try:
		print screen.terminal_size
	except IOError:
		pass

Screen(loop)