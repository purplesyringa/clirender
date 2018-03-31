from node import Node

class NoDefault(object):
	pass

def fromXml(elem, slots, name, defines, container):
	class FromXml(Node):
		def __init__(self, **attrs):
			if self.text_container:
				super(FromXml, self).__init__(value=attrs["value"])
				attrs[""] = attrs["value"]
				del attrs["value"]
			elif self.container:
				super(FromXml, self).__init__(children=attrs["children"])

				if len(attrs["children"]) > 1:
					raise ValueError("Too many nodes in <%s>" % name)
				elif len(attrs["children"]) == 1:
					attrs[""] = attrs["children"][0]
					del attrs["children"]
				else:
					raise ValueError("Too less nodes in <%s>" % name)


			self.slots = dict(**slots)
			for attr, value in attrs.items():
				if attr not in self.slots and attr != "":
					raise ValueError("Unexpected slot :%s" % attr)

				self.slots[attr] = value

			for slot in self.slots.values():
				if isinstance(slot, NoDefault):
					raise ValueError("Required slot :%s not passed" % slot)

		def render(self, *args, **kwargs):
			from ..xml_parser import handleElement
			node = handleElement(elem, defines=defines, slots=self.slots)[0]

			node.render_offset = self.render_offset
			node.render_boundary_left_top = self.render_boundary_left_top
			node.render_boundary_right_bottom = self.render_boundary_right_bottom
			node.parent = self.parent
			node.render_stretch = self.render_stretch

			return node.render(*args, **kwargs)

	FromXml.text_container = container == "text"
	FromXml.container = container == "node"

	return FromXml