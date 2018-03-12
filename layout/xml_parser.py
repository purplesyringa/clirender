from lxml import etree

import nodes

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

		children = filter(lambda child: child.tag != "Slot" and child.tag != etree.Comment, children)

		if len(children) != 1:
			raise ValueError("<Define> must have exactly one child")

		defines[node.attrib["name"]] = dict(node=children[0], slots=slots)

	result = fromNode(root, defines, {})
	if len(result) == 0:
		raise ValueError("No root node")
	elif len(result) > 1:
		raise ValueError("Several root nodes")

	return result[0]

def fromNode(node, defines, slots):
	if node.tag == "Define":
		return []
	elif node.tag == etree.Comment:
		return []
	elif node.tag == "Slot":
		name = node.attrib.get("name", "")
		if name not in slots and name not in special_slots:
			raise ValueError("Unknown slot :%s" % name)

		slot = slots.get(name, special_slots.get(name))

		if isinstance(slot, str) or isinstance(slot, unicode):
			raise ValueError("Slot :%s cannot be a string, only a node" % name)

		return fromNode(slot["node"], defines, slot["slots"])

	attrs, inheritable, all_attrs = filterAttrs(node, slots)

	if node.tag == "Range":
		return handleRange(node, defines, slots, attrs)
	elif node.tag in defines:
		return handleDefine(node, defines, slots, all_attrs)

	try:
		ctor = getattr(nodes, node.tag)
	except AttributeError:
		raise ValueError("Unknown node %s" % node.tag)

	children = filter(lambda child: child.tag != etree.Comment, node)

	if ctor.text_container:
		value = getInnerText(node, slots)

		# Only text inside
		node = ctor(value=value, **attrs)
		node.inheritable = inheritable
		return [node]
	if node.text is not None and node.text.strip() != "":
		raise ValueError("%s should not contain text" % node.tag)

	if len(children) > 0:
		# There are some nodes inside
		if ctor.container:
			node = ctor(children=filter(lambda node: node is not None, concat(map(lambda child: fromNode(child, defines, slots), node))), **attrs)
			node.inheritable = inheritable
			return [node]
		else:
			raise ValueError("%s is not a container" % node.tag)

	node = ctor(**attrs)
	node.inheritable = inheritable
	return [node]

def getInnerText(node, slots):
	if node.tag == "Slot":
		name = node.attrib.get("name", "")

		if name not in slots and name not in special_slots:
			raise ValueError("Unknown slot :%s" % name)

		slot = slots.get(name, special_slots.get(name))

		if isinstance(slot, str) or isinstance(slot, unicode):
			return slots[name]
		elif slot["node"].tag == "Slot":
			# Recursive slot
			return getInnerText(slot["node"], slot["slots"])
		else:
			raise ValueError("Slot :%s is a node, so it cannot be used inside text container" % name)

	value = ""

	for child in node.xpath("child::node()"):
		if isinstance(child, str) or isinstance(child, unicode):
			value += child
		elif child.tag == etree.Comment:
			pass
		elif child.tag == "Slot":
			value += getInnerText(child, slots)
		else:
			raise ValueError("Text container must contain text")

	return value

def filterAttrs(node, slots):
	attrs = {}
	inheritable = {}
	all_attrs = {}

	for name, value in node.attrib.items():
		if name[0] == ":": # Attribute name starts with colon, use slot
			try:
				value = slots[value]
			except KeyError:
				try:
					value = special_slots[value]
				except KeyError:
					raise ValueError("Unknown slot :%s" % value)

			name = name[1:]

		if name.startswith("inherit-"):
			inheritable[name[len("inherit-"):]] = value
		else:
			attrs[name] = value

		all_attrs[name] = value

	return attrs, inheritable, all_attrs

def handleRange(node, defines, slots, attrs):
	slot = attrs.get("slot", None)

	try:
		from_ = int(attrs["from"])
	except ValueError:
		raise ValueError("'from' attribute of <Range> must be an integer")
	except KeyError:
		raise ValueError("<Range> must contain 'from' attribute")

	try:
		to = int(attrs["to"])
	except ValueError:
		raise ValueError("'to' attribute of <Range> must be an integer")
	except KeyError:
		raise ValueError("<Range> must contain 'to' attribute")

	try:
		step = int(attrs["step"])
	except ValueError:
		raise ValueError("'step' attribute of <Range> must be an integer")
	except KeyError:
		step = 1

	res = []
	new_slots = dict(**slots)
	for i in range(from_, to, step):
		if slot is not None:
			new_slots[slot] = str(i)
		for child in node:
			subchildren = fromNode(child, defines, new_slots)
			for subchild in subchildren:
				container = nodes.Container(children=[subchild])
				res.append(container)
	return res

def handleDefine(node, defines, slots, all_attrs):
	if len(node) == 1:
		if node[0].tag == "Range":
			raise ValueError("Cannot guarantee that <Range> will result in 0 or 1 node, which are allowed as <Slot /> inside <Define>")
		elif node.text is not None and node.text.strip() != "":
			raise ValueError("Only 1 node allowed as <Slot /> inside <Define>")

		all_attrs[""] = dict(node=node[0], slots=slots)
	elif node.text is not None and node.text.strip() != "":
		all_attrs[""] = node.text
	elif len(node) > 1:
		raise ValueError("Only 1 node allowed as <Slot /> inside <Define>")

	slots = defines[node.tag]["slots"]

	for name, value in slots.items():
		# Non-optional slot not passed
		if value is NoDefault and name not in all_attrs:
			raise ValueError("Slot :%s without default value not filled when passed to <Define name='%s'>" % (name, node.tag))

	for name, value in all_attrs.items():
		if name not in slots:
			raise ValueError("Unknown slot :%s passed to <Define name='%s'> as slot" % (name, node.tag))
		slots[name] = value

	return fromNode(defines[node.tag]["node"], defines, slots)

def concat(arrs):
	res = []
	for arr in arrs:
		res += arr
	return res