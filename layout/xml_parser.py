from lxml import etree

import nodes

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
			if child.tag == "Slot":
				name = child.attrib["define"]
				slots[name] = child.attrib.get("default", None)

		children = filter(lambda child: child.tag != "Slot" and child.tag != etree.Comment, children)

		if len(children) != 1:
			raise ValueError("<Define> must have exactly one child")

		defines[node.attrib["name"]] = dict(node=children[0], slots=slots)

	return fromNode(root, defines, {})

def fromNode(node, defines, slots):
	if node.tag == "Define":
		return None
	elif node.tag == etree.Comment:
		return None

	attrs = {}
	inheritable = {}
	all_attrs = {}

	for name, value in node.attrib.items():
		if name[0] == ":": # Attribute name starts with colon, use slot
			try:
				value = slots[value]
			except KeyError:
				raise ValueError("Unknown slot %s" % value)

			name = name[1:]

		if name.startswith("inherit-"):
			inheritable[name[len("inherit-"):]] = value
		else:
			attrs[name] = value

		all_attrs[name] = value

	# Parse defines nodes
	if node.tag in defines:
		slots = defines[node.tag]["slots"]

		for name, value in slots.items():
			# Non-optional slot not passed
			if value is None and name not in all_attrs:
				raise ValueError("Slot :%s without default value not filled when passed to <Define name='%s'>" % (name, node.tag))

		for name, value in all_attrs.items():
			if name not in slots:
				raise ValueError("Unknown attribute %s passed to <Define name='%s'> as slot" % (name, node.tag))
			slots[name] = value

		return fromNode(defines[node.tag]["node"], defines, slots)

	try:
		ctor = getattr(nodes, node.tag)
	except AttributeError:
		raise ValueError("Unknown node %s" % node.tag)

	children = filter(lambda child: child.tag != etree.Comment, node)

	if ctor.text_container:
		value = ""
		for child in node.xpath("child::node()"):
			if isinstance(child, str) or isinstance(child, unicode):
				value += child
			elif child.tag == etree.Comment:
				pass
			elif child.tag == "Slot" and "name" in child.attrib:
				name = child.attrib["name"]
				try:
					value += slots[name]
				except KeyError:
					raise ValueError("Unknown slot :%s" % name)
			else:
				raise ValueError("Text container must contain text")

		# Only text inside
		node = ctor(value=value, **attrs)
		node.inheritable = inheritable
		return node
	if node.text is not None and node.text.strip() != "":
		raise ValueError("%s should not contain text" % node.tag)

	if len(children) > 0:
		# There are some nodes inside
		if ctor.container:
			node = ctor(children=filter(lambda node: node is not None, map(lambda child: fromNode(child, defines, slots), node)), **attrs)
			node.inheritable = inheritable
			return node
		else:
			raise ValueError("%s is not a container" % node.tag)

	node = ctor(**attrs)
	node.inheritable = inheritable
	return node