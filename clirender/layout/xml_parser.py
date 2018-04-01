from lxml import etree

import nodes

special_slots = {
	"__unset__": None
}

NoDefault = nodes.NoDefault

def gatherLibs(node):
	if isinstance(node, (str, unicode)):
		parser = etree.XMLParser(recover=True)
		node = etree.fromstring(node, parser=parser)

	libs = []
	for node in node.findall("Use"):
		if "lib" in node.attrib:
			libs.append(node.attrib["lib"])
	return libs

def fromXml(code, additional_nodes={}):
	parser = etree.XMLParser(recover=True)
	root = etree.fromstring(code, parser=parser)

	define_nodes = root.findall("Define")

	for node in define_nodes:
		if "name" not in node.attrib:
			raise ValueError("<Define> without 'name' attribute")
		elif getattr(nodes, node.tag, None) is not None:
			raise ValueError("Cannot <Define> core node %s" % node.tag)
		elif additional_nodes.get(node.tag, None) is not None:
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
					slot = child.attrib.get(":default", NoDefault)
					if slot is not NoDefault:
						if slot != "__unset__":
							raise ValueError("Deprecated: No slot except :__unset__ can be used for :default")
						slots[name] = evaluate(slot, slots={})

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

		defines[node.attrib["name"]] = nodes.fromXml(elem=children[0], slots=slots, defines=defines, name=node.attrib["name"], container=container, additional_nodes=additional_nodes)

	return handleElement(root, defines, slots={}, additional_nodes=additional_nodes)[0]

def handleElement(node, defines, slots, additional_nodes):
	if node.tag in ["Define", "Use"]:
		return []
	elif node.tag is etree.Comment:
		return []
	elif node.tag == "Slot":
		if "define" in node.attrib:
			return []

		name = node.attrib.get("name", "")
		if name not in slots:
			raise ValueError("Unknown slot :%s" % name)

		value = evaluate(name, slots=slots)
		if isinstance(value, (str, unicode)):
			raise ValueError("Unexpected string slot :%s" % name)
		elif value is NoDefault:
			raise ValueError("Required slot :%s was not passed (from <%s>)" % (name, node.tag))

		return [value]

	attrs = {}
	inheritable = {}
	for attr, value in node.attrib.items():
		if attr.startswith(":"):
			attr = attr[1:]
			try:
				slot = evaluate(value, slots=slots)
				if slot is NoDefault:
					raise ValueError("Required slot :%s was not passed (from <%s>)" % (value, node.tag))

				value = slot
			except KeyError:
				raise ValueError("Unknown slot :%s" % value)

		if attr.startswith("inherit-"):
			attr = attr[len("inherit-"):]
			inheritable[attr] = value
		else:
			# Escape keywods
			if attr in ("from", "is", "with", "else"):
				attr += "_"

			attrs[attr] = value

	ctor = getattr(nodes, node.tag, None)
	if ctor is None:
		ctor = defines.get(node.tag, None)
	if ctor is None:
		ctor = additional_nodes.get(node.tag, None)
	if ctor is None:
		raise ValueError("Unknown node <%s>" % node.tag)

	if issubclass(ctor, nodes.Generator):
		return handleGenerator(node, defines, slots, ctor=ctor, attrs=attrs, inheritable=inheritable, additional_nodes=additional_nodes)

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
			children += handleElement(child, defines, slots, additional_nodes=additional_nodes)

		result = ctor(children=children, **attrs)
	else:
		if len(node) > 0:
			raise ValueError("Nodes inside <%s>" % node.tag)
		elif node.text is not None and node.text.strip() != "":
			raise ValueError("Text inside <%s>" % node.tag)

		result = ctor(**attrs)

	result.slots = slots
	result.defines = defines
	result.additional_nodes = additional_nodes
	result.inheritable = inheritable
	return [result]

def handleGenerator(node, defines, slots, ctor, attrs, inheritable, additional_nodes):
	if ctor.text_container:
		node = ctor(value=getTextInside(node, slots, allow_nodes=False), slots=slots, **attrs)
	elif ctor.container:
		node = ctor(children=list(node), slots=slots, **attrs)
	else:
		node = ctor(slots=slots, **attrs)

	node.defines = defines
	node.additional_nodes = additional_nodes
	node.inheritable = inheritable
	return [node]

def getTextInside(node, slots, allow_nodes=False):
	text = ""
	had_nodes = False

	for item in node.xpath("child::node()"):
		if isinstance(item, (str, unicode)):
			text += item

			if allow_nodes is None and text.strip() != "" and had_nodes:
				raise ValueError("Nodes and text inside <%s>" % node.tag)
		elif item.tag is etree.Comment:
			pass
		elif item.tag == "Slot":
			name = item.attrib.get("name", "")
			if name in slots:
				value = evaluate(name, slots=slots)
				if value is NoDefault:
					raise ValueError("Required slot :%s was not passed (from <%s>)" % (name, node.tag))
				elif isinstance(value, (str, unicode)):
					text += value
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

def evaluate(expr, slots):
	if expr == "":
		return slots[""]

	all_slots = {"__builtins__": None}
	all_slots.update(slots)
	all_slots.update(special_slots)

	return eval(expr, all_slots)