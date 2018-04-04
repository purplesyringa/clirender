from nodes import Node, Generator

class NodeAPI(object):
	def getBoundaryBox(self):
		node = storage[self]
		if isinstance(node, Node):
			return node.getBoundaryBox()
		else:
			raise ValueError("getBoundaryBox(): Not defined on %s" % type(node))

	@property
	def childNodes(self):
		node = storage[self]
		if isinstance(node, Node):
			return map(createAPI, node._children)
		elif isinstance(node, Generator):
			return map(createAPI, node.generate())
		else:
			raise ValueError("childNodes: Not defined on %s" % type(node))

	@property
	def children(self):
		node = storage[self]
		if isinstance(node, Node):
			return map(createAPI, node.children)
		elif isinstance(node, Generator):
			return map(createAPI, self._get_children_recursively(node))
		else:
			raise ValueError("children: Not defined on %s" % type(node))

	def _get_children_recursively(self, generator):
		res = []
		for node in generator.generate():
			if isinstance(node, Generator):
				res += self._get_children_recursively(node)
			else:
				res.append(node)
		return res


# storage[self] is a way to simulate private scope, so that Node or Generator
# couldn't be accessed from outside
storage = dict()

def createAPI(node):
	class LocalNodeAPI(NodeAPI):
		def __init__(self):
			storage[self] = node
			super(LocalNodeAPI, self).__init__()

	return LocalNodeAPI()