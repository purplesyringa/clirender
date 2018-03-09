import xml.dom
from xml.etree import ElementTree

import nodes

def fromXml(code):
	parser = ElementTree.XMLParser()
	eoor = ElementTree.fromstring(code, parser=parser)

	define_nodes = root.findall("Define")

	for node in define_nodes:
		if "name" not in node.attrib:
			raise ValueError("<Define> without 'name' attribute")
		elif len(node) != 1:
			raise ValueError("<Define> must have exactly one child")
		elif getattr(nodes, node.tag, None) is not None:
			raise ValueError("Cannot <Define> core node %s" % node.tag)

	define_nodes.sort(key=lambda define: define.attrib["name"])
	for i in range(len(define_nodes) - 1):
		a = define_nodes[i + 0].attrib["name"]
		b = define_nodes[i + 1].attrib["name"]
		if a == b:
			raise ValueError("Non-unique <Define name='%s'>" % a)

	defines = {}
	for node in define_nodes:
		defines[node.attrib["name"]] = node[0]

	return fromNode(root, defines)

def fromNode(node, defines):
	if node.tag == "Define":
		return None

	if node.tag in defines:
		return fromNode(defines[node.tag], defines)

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
			node = ctor(children=filter(lambda node: node is not None, map(lambda child: fromNode(child, defines), node)), **attrs)
			node.inheritable = inheritable
			return node
		else:
			raise ValueError("%s is not a container" % node.tag)

	node = ctor(**attrs)
	node.inheritable = inheritable
	return node