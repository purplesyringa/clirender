from nodes import Node, Generator

class NodeAPI(object):
	def getBoundaryBox(self):
		node = storage[self]
		if isinstance(node, Node):
			return node.getBoundaryBox()
		else:
			raise self._unexpectedType("getBoundaryBox()")

	@property
	def childNodes(self):
		node = storage[self]
		if isinstance(node, Node):
			return map(createAPI, node._children)
		elif isinstance(node, Generator):
			return map(createAPI, node.generate())
		else:
			raise self._unexpectedType("childNodes")

	@property
	def children(self):
		node = storage[self]
		if isinstance(node, Node):
			return map(createAPI, node.children)
		elif isinstance(node, Generator):
			return map(createAPI, self._get_children_recursively(node))
		else:
			raise self._unexpectedType("children")

	def _get_children_recursively(self, generator):
		res = []
		for node in generator.generate():
			if isinstance(node, Generator):
				res += self._get_children_recursively(node)
			else:
				res.append(node)
		return res


	def _unexpectedType(self, callee):
		node = storage[self]
		return ValueError("%s: Not defined on %s" % (callee, type(node)))


# storage[self] is a way to simulate private scope, so that Node or Generator
# couldn't be accessed from outside
storage = dict()

def createAPI(node):
	class LocalNodeAPI(NodeAPI):
		def __init__(self):
			storage[self] = node
			super(LocalNodeAPI, self).__init__()

	return LocalNodeAPI()