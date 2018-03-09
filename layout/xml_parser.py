import xml.dom
from xml.etree import ElementTree

import nodes

def fromXml(code):
	return fromNode(ElementTree.fromstring(code))

def fromNode(node):
	attrs = {}
	inheritable = {}

	for name, value in node.attrib.items():
		if name.startswith("inherit-"):
			inheritable[name[len("inherit-"):]] = value
		else:
			attrs[name] = value

	try:
		ctor = getattr(nodes, node.tag)
	except AttributeError:
		raise ValueError("Unknown node %s" % node.tag)

	if ctor.text_container:
		if len(node) == 0:
			# Only text inside
			node = ctor(value=node.text or "", **attrs)
			node.inheritable = inheritable
			return node
		else:
			raise ValueError("Text container must contain text")

	if node.text is not None and node.text.strip() != "":
		raise ValueError("%s should not contain text" % node.tag)

	if len(node) > 0:
		# There are some nodes inside
		if ctor.container:
			node = ctor(children=map(fromNode, node), **attrs)
			node.inheritable = inheritable
			return node
		else:
			raise ValueError("%s is not a container" % node.tag)

	node = ctor(**attrs)
	node.inheritable = inheritable
	return node