import xml.dom
import xml.dom.minidom

import nodes

def fromXml(code):
	parsed = xml.dom.minidom.parseString(code)

	children = filter(lambda child: child.nodeType != xml.dom.Node.COMMENT_NODE, parsed.childNodes)
	if len(children) == 0:
		raise ValueError("Empty document: no root nodes")
	elif len(children) > 1:
		raise ValueError("Several root nodes present")

	return fromNode(children[0])

def fromNode(node):
	if node.nodeType == xml.dom.Node.ELEMENT_NODE:
		attrs = {}
		for i in range(node.attributes.length):
			attr = node.attributes.item(i)
			attrs[attr.nodeName] = attr.nodeValue

		try:
			ctor = getattr(nodes, node.tagName)
		except AttributeError:
			raise ValueError("Unknown node %s" % node.tagName)

		children = filter(lambda child: child.nodeType != xml.dom.Node.COMMENT_NODE, node.childNodes)

		text_nodes = filter(lambda child: child.nodeType == xml.dom.Node.TEXT_NODE, children)

		if ctor.text_container:
			if text_nodes == children:
				# Only text inside
				value = "".join(map(lambda node: node.nodeValue, text_nodes))
				return ctor(value=value, **attrs)
			else:
				raise ValueError("Text container must contain text")

		text_nodes = filter(lambda child: child.nodeValue.strip() != "", text_nodes)
		if len(text_nodes) > 0:
			raise ValueError("%s should not contain text" % node.tagName)

		# Remove empty text nodes
		children = filter(lambda child: child.nodeType != xml.dom.Node.TEXT_NODE or child.nodeValue.strip() != "", children)

		if len(children) > 0:
			# There are some nodes inside
			if ctor.container:
				return ctor(children=map(fromNode, children), **attrs)
			else:
				raise ValueError("%s is not a container" % node.tagName)

		return ctor(**attrs)
	else:
		raise ValueError("Unknown node type %s" % node.nodeType)