import sys

from colorama import Fore, Back, Style

def dump(node, indent=""):
	name = type(node).__name__

	children = getChildren(node)

	sys.stdout.write(indent + "<")
	sys.stdout.write(Fore.YELLOW + name + Style.RESET_ALL)
	dumpAttrs(node)
	sys.stdout.write(">" + ("\n" if children != [] else ""))

	for child in children:
		dump(child, indent=indent + " ")

	if hasattr(node, "value"):
		sys.stdout.write(Fore.GREEN + node.value + Style.RESET_ALL)

	sys.stdout.write((indent if children != [] else "") + "</")
	sys.stdout.write(Fore.YELLOW + name + Style.RESET_ALL)
	sys.stdout.write(">\n")

def dumpAttrs(node):
	attr_names = node.__dict__.keys()
	attr_names = filter(lambda name: name not in ["parent", "child", "children", "value", "inheritable"] and not name.startswith("render_"), attr_names)


	for attr in attr_names:
		if isinstance(getattr(node, attr), bool) or getattr(node, attr) is None:
			if getattr(node, attr):
				sys.stdout.write(" " + Fore.BLUE + attr + Style.RESET_ALL)
			continue

		sys.stdout.write(" " + Fore.BLUE + attr + Style.RESET_ALL)
		sys.stdout.write("=" + Fore.RED)
		if isinstance(getattr(node, attr), str) or isinstance(getattr(node, attr), unicode):
			sys.stdout.write("\"" + getattr(node, attr) + "\"")
		else:
			sys.stdout.write(str(getattr(node, attr)))
		sys.stdout.write(Style.RESET_ALL)


	inheritable = node.inheritable
	for name, value in inheritable.items():
		if isinstance(value, bool) or value is None:
			if value:
				sys.stdout.write(" " + Back.MAGENTA + "inherit-" + name + Style.RESET_ALL)
			continue

		sys.stdout.write(" " + Back.MAGENTA + "inherit-" + name + Style.RESET_ALL)
		sys.stdout.write("=" + Fore.RED)
		if isinstance(value, str) or isinstance(value, unicode):
			sys.stdout.write("\"" + value + "\"")
		else:
			sys.stdout.write(str(value))
		sys.stdout.write(Style.RESET_ALL)


def getChildren(node):
	try:
		return node.children
	except AttributeError:
		pass
	try:
		return [node.child]
	except AttributeError:
		pass
	return []