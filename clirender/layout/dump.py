import sys

from colorama import Fore, Back, Style
from clirender.screen import Screen
screen = Screen()

def dump(node, indent=""):
	name = type(node).__name__

	if name == "Container" and node.type is not None:
		func = "dump" + node.type[0].upper() + node.type[1:]
		if func in globals():
			globals()[func](node, indent)
			dump(node.child, indent=indent + " ")
			return

	children = getChildren(node)

	sys.stdout.write(indent + "<")
	sys.stdout.write(Fore.YELLOW + name + Style.RESET_ALL)
	dumpAttrs(node)
	sys.stdout.write(">" + ("\n" if children != [] else ""))

	for child in children:
		dump(child, indent=indent + " ")

	if hasattr(node, "value"):
		dumpText(node.text_slots)

	sys.stdout.write((indent if children != [] else "") + "</")
	sys.stdout.write(Fore.YELLOW + name + Style.RESET_ALL)
	sys.stdout.write(">\n")

def dumpAttrs(node):
	attr_names = node.__dict__.keys()
	attr_names = filter(lambda name: name not in ["parent", "child", "children", "value", "inheritable", "text_slots"] and not name.startswith("render_"), attr_names)


	for attr in attr_names:
		if isinstance(getattr(node, attr), bool) or getattr(node, attr) is None:
			if getattr(node, attr):
				sys.stdout.write(" " + Fore.BLUE + attr + Style.RESET_ALL)
			continue

		sys.stdout.write(" " + Fore.BLUE + attr + Style.RESET_ALL)
		sys.stdout.write("=" + Fore.RED)
		if isinstance(getattr(node, attr), str) or isinstance(getattr(node, attr), unicode):
			sys.stdout.write("\"" + formatAttr(attr, getattr(node, attr)) + "\"")
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
			sys.stdout.write("\"" + formatAttr(name, value) + "\"")
		else:
			sys.stdout.write(str(value))
		sys.stdout.write(Style.RESET_ALL)

def formatAttr(name, value):
	if name in ["color", "bg"]:
		return formatColor(value)

	return value

def formatColor(color):
	parts = map(lambda part: part.strip(), color.split("|"))
	values = []
	for part in parts:
		try:
			values.append(screen.colorize(text=" ", bg=part) + screen.colorize(text=" " + part, fg=part))
		except ValueError:
			values.append(part)
	return " | ".join(values)

def dumpRange(node, indent=""):
	if node.range_begin:
		sys.stdout.write(indent + Fore.CYAN + "#(range %s)" % node.range_value + Style.RESET_ALL + "\n")

def dumpDefine(node, indent=""):
	sys.stdout.write(indent + Fore.CYAN + "#(define %s)" % node.define_name + Style.RESET_ALL + "\n")

def dumpSlot(node, indent=""):
	sys.stdout.write(indent + Fore.CYAN + "#(slot)" + Style.RESET_ALL + "\n")

def dumpText(slots):
	for val in slots:
		if isinstance(val, str) or isinstance(val, unicode):
			sys.stdout.write(Fore.GREEN + val + Style.RESET_ALL)
		else:
			sys.stdout.write(Fore.CYAN + "#(slot")
			if val["name"]:
				sys.stdout.write(" %s=" % val["name"])
			else:
				sys.stdout.write("=")
			sys.stdout.write(Style.RESET_ALL)

			dumpText(val["value"])

			sys.stdout.write(Fore.CYAN + ")" + Style.RESET_ALL)

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