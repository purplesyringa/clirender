from lxml import etree

import nodes
from slot import Slot

special_slots = {
	"__unset__": None
}

class NoDefault(object):
	pass

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

		children = filter(lambda child: (child.tag != "Slot" or "define" not in child.attrib) and child.tag != etree.Comment, children)

		if len(children) != 1:
			raise ValueError("<Define> must have exactly one child")

		defines[node.attrib["name"]] = dict(node=children[0], slots=slots)

	result = fromNode(root, defines, parent=None)
	if len(result) == 0:
		raise ValueError("No root node")
	elif len(result) > 1:
		raise ValueError("Several root nodes")

	return result[0]

def fromNode(node, defines, parent):
	if node.tag == "Define":
		return []
	elif node.tag == etree.Comment:
		return []
	elif node.tag == "Slot":
		name = node.attrib.get("name", "")

		if name in special_slots:
			slot = special_slots[name]
			if isinstance(slot, str) or isinstance(slot, unicode):
				raise ValueError("Slot :%s cannot be a string, only a node" % name)

			return fromNode(slot["node"], defines, parent=parent)
		else:
			return [Slot(name, context=parent)]

	attrs, inheritable, all_attrs = filterAttrs(node, context=parent)

	if node.tag in defines:
		return handleDefine(node, defines, all_attrs, parent=parent)

	for name in attrs.keys():
		if name in ["from"]:
			attrs[name + "_"] = attrs[name]
			del attrs[name]

	try:
		ctor = getattr(nodes, node.tag)
	except AttributeError:
		raise ValueError("Unknown node %s" % node.tag)

	children = filter(lambda child: child.tag != etree.Comment, node)

	if ctor.text_container:
		value = getInnerText(node, context=parent)

		# Only text inside
		node = ctor(value=value, **attrs)
		node.inheritable = inheritable
		return [node]
	if node.text is not None and node.text.strip() != "":
		raise ValueError("%s should not contain text" % node.tag)

	if len(children) > 0:
		# There are some nodes inside
		if ctor.container:
			xnode = ctor(**attrs)
			if isinstance(xnode, nodes.Generator):
				xnode.children = wrapGenerator(node.tag, node, defines)
			else:
				xnode.children = [node for node in concat(fromNode(child, defines, parent=xnode) for child in node) if node is not None]
			xnode.inheritable = inheritable
			return [xnode]
		else:
			raise ValueError("%s is not a container" % node.tag)

	node = ctor(**attrs)
	node.inheritable = inheritable
	return [node]

def getInnerText(node, context):
	value_slots = []

	for child in node.xpath("child::node()"):
		if isinstance(child, str) or isinstance(child, unicode):
			value_slots.append(child)
		elif child.tag == etree.Comment:
			pass
		elif child.tag == "Slot":
			name = child.attrib.get("name", "")
			value_slots.append(Slot(name, context=context))
		else:
			raise ValueError("Text container must contain text")

	return value_slots

def filterAttrs(node, context):
	attrs = {}
	inheritable = {}
	all_attrs = {}

	for name, value in node.attrib.items():
		if name[0] == ":": # Attribute name starts with colon, use slot
			value = Slot(value, context=context)
			name = name[1:]

		if name.startswith("inherit-"):
			inheritable[name[len("inherit-"):]] = value
		else:
			attrs[name] = value

		all_attrs[name] = value

	return attrs, inheritable, all_attrs

def handleDefine(node, defines, all_attrs, parent):
	if len(node) == 1:
		if node[0].tag == "Range":
			raise ValueError("Cannot guarantee that <Range> will result in 0 or 1 node, which are allowed as <Slot /> inside <Define>")
		elif node.text is not None and node.text.strip() != "":
			raise ValueError("Only 1 node allowed as <Slot /> inside <Define>")

		child = fromNode(node[0], defines, parent=parent)[0]
		if isinstance(child, Slot):
			all_attrs[""] = child
		else:
			all_attrs[""] = dict(node=child, context=parent)
	elif node.text is not None and node.text.strip() != "":
		all_attrs[""] = node.text
	elif len(node) > 1:
		raise ValueError("Only 1 node allowed as <Slot /> inside <Define>")


	slots = dict(**defines[node.tag]["slots"])

	for name, value in slots.items():
		# Non-optional slot not passed
		if value is NoDefault and name not in all_attrs:
			raise ValueError("Slot :%s without default value not filled when passed to <Define name='%s'>" % (name, node.tag))

	for name, value in all_attrs.items():
		if name not in slots:
			raise ValueError("Unknown slot :%s passed to <Define name='%s'> as slot" % (name, node.tag))
		slots[name] = value

	# We can only use context of the parent, so if the root of the <Define>
	# uses slots, it will use the wrong parent for context. Instead, we can
	# wrap it in a <Container> and use the container as context.
	container = nodes.Container()
	container.type = "define"
	container.slot_context = slots
	container.inherit_slots = False

	xnode = fromNode(defines[node.tag]["node"], defines, parent=container)
	container.children = xnode
	return [container]

def wrapGenerator(type, node, defines):
	# We can only use context of the parent, so if the generator changes
	# slots, it will use the wrong parent for context. Instead, we can
	# wrap it in a <Container> and use the container as context.

	res = []
	for child in node:
		container = nodes.Container()
		container.type = type
		container.children = fromNode(child, defines, parent=container)
		res.append(container)

	return res

def concat(arrs):
	res = []
	for arr in arrs:
		res += arr
	return res