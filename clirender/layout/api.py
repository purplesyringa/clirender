from nodes import Node

class NodeAPI(object):
	def getBoundingBox(self):
		node = storage[self]
		if isinstance(node, Node):
			return node.getBoundingBox()
		else:
			raise ValueError("getBoundingBox(): Not defined on %s" % type(node))


# storage[self] is a way to simulate private scope, so that Node or Generator
# couldn't be accessed from outside
storage = dict()

def createAPI(node):
	class LocalNodeAPI(NodeAPI):
		def __init__(self):
			storage[self] = node
			super(LocalNodeAPI, self).__init__()

	return LocalNodeAPI()