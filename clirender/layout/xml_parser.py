from lxml import etree

import nodes
from slot import Slot

special_slots = {
	"__unset__": None
}

NoDefault = nodes.NoDefault

def fromXml(code):
	parser = etree.XMLParser(recover=True)
	root = etree.fromstring(code, parser=parser)

	define_nodes = root.findall("Define")

	for node in define_nodes:
		if "name" not in node.attrib:
			raise ValueError("<Define> without 'name' attribute")
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
		slots = {}
		container = ""

		children = list(node)
		for child in children:
			if child.tag == "Slot" and "define" in child.attrib:
				name = child.attrib["define"]
				if name in special_slots:
					raise ValueError("Defining special slot :%s" % name)

				slots[name] = child.attrib.get("default", NoDefault)
				if slots[name] is NoDefault:
					if ":default" in child.attrib:
						slot_name = child.attrib[":default"]
						slots[name] = slots.get(slot_name, special_slots.get(slot_name, NoDefault))

				if name == "":
					if "container" not in child.attrib:
						raise ValueError("Deprecated: Set container=node or container=text for <Define name='' />")
					elif child.attrib["container"].lower() == "node":
						container = "node"
					elif child.attrib["container"].lower() == "text":
						container = "text"
					else:
						raise ValueError("Only 'node' or 'text' values are accepted for 'container' attribute of <Define name='' />")

		children = filter(lambda child: (child.tag != "Slot" or "define" not in child.attrib) and child.tag != etree.Comment, children)

		if len(children) != 1:
			raise ValueError("<Define> must have exactly one child")
		if children[0].tag == "Range":
			raise ValueError("<Define> must have exactly one child: cannot guarantee that <Range> is always one child")

		defines[node.attrib["name"]] = nodes.fromXml(elem=children[0], slots=slots, defines=defines, name=node.attrib["name"], container=container)

	return handleElement(root, defines, slots={})[0]


def handleElement(node, defines, slots):
	if node.tag == "Define":
		return []
	elif node.tag is etree.Comment:
		return []
	elif node.tag == "Slot":
		if "define" in node.attrib:
			return []

		name = node.attrib.get("name", "")
		if name not in slots:
			raise ValueError("Unknown slot :%s" % name)

		if isinstance(slots[name], str) or isinstance(slots[name], unicode):
			raise ValueError("Unexpected string slot :%s" % name)
		elif slots[name] is NoDefault:
			raise ValueError("Required slot :%s was not passed (from <%s>)" % (name, node.tag))

		return [slots[name]]

	attrs = {}
	inheritable = {}
	for attr, value in node.attrib.items():
		if attr.startswith(":"):
			attr = attr[1:]
			try:
				if slots[value] is NoDefault:
					raise ValueError("Required slot :%s was not passed (from <%s>)" % (value, node.tag))

				value = slots[value]
			except KeyError:
				raise ValueError("Unknown slot :%s" % value)

		if attr.startswith("inherit-"):
			attr = attr[len("inherit-"):]
			inheritable[attr] = value
		else:
			# Escape keywods
			if attr in ("from"):
				attr += "_"

			attrs[attr] = value

	ctor = getattr(nodes, node.tag, None)
	if ctor is None:
		ctor = defines.get(node.tag, None)
	if ctor is None:
		raise ValueError("Unknown node <%s>" % node.tag)

	if issubclass(ctor, nodes.Generator):
		return handleGenerator(node, defines, slots, ctor=ctor, attrs=attrs, inheritable=inheritable)

	result = None
	if ctor.text_container:
		text_inside = getTextInside(node, slots=slots)

		result = ctor(value=text_inside, **attrs)
	elif ctor.container:
		text_inside = getTextInside(node, slots=slots, allow_nodes=True)
		if text_inside.strip() != "":
			raise ValueError("Text inside <%s>" % node.tag)

		children = []
		for child in node:
			children += handleElement(child, defines, slots)

		result = ctor(children=children, **attrs)
	else:
		if len(node) > 0:
			raise ValueError("Nodes inside <%s>" % node.tag)
		elif node.text is not None and node.text.strip() != "":
			raise ValueError("Text inside <%s>" % node.tag)

		result = ctor(**attrs)

	result.inheritable = inheritable
	return [result]

def handleGenerator(node, defines, slots, ctor, attrs, inheritable):
	node = ctor(children=list(node), **attrs)
	node.inheritable = inheritable
	return node.generate(slots, defines)

def getTextInside(node, slots, allow_nodes=False):
	text = ""
	had_nodes = False

	for item in node.xpath("child::node()"):
		if isinstance(item, str) or isinstance(item, unicode):
			text += item

			if allow_nodes is None and text.strip() != "" and had_nodes:
				raise ValueError("Nodes and text inside <%s>" % node.tag)
		elif item.tag is etree.Comment:
			pass
		elif item.tag == "Slot":
			name = item.attrib.get("name", "")
			if name in slots:
				if slots[name] is NoDefault:
					raise ValueError("Required slot :%s was not passed (from <%s>)" % (name, node.tag))
				elif isinstance(slots[name], str) or isinstance(slots[name], unicode):
					text += slots[name]
				elif allow_nodes is None and had_nodes:
					raise ValueError("Nodes and text inside <%s>" % node.tag)
				elif allow_nodes is False:
					raise ValueError("Nodes inside <%s>" % node.tag)
			else:
				raise ValueError("Unknown slot :%s" % name)
		else:
			if allow_nodes is None and text.strip() != "":
				raise ValueError("Nodes and text inside <%s>" % node.tag)
			elif allow_nodes is False:
				raise ValueError("Nodes inside <%s>" % node.tag)

			had_nodes = True

	return text