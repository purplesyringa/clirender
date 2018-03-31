from node import Node

class NoDefault(object):
	pass

def fromXml(node, slots, name, defines):
	class FromXml(Node):
		text_container = True
		container = True

		def __init__(self, _value=None, **attrs):
			super(FromXml, self).__init__(value=_value)
			self.node = node

			if isinstance(_value, str) or isinstance(_value, unicode):
				attrs[""] = _value
			elif len(_value) > 1:
				raise ValueError("Too many nodes in <%s>" % name)
			elif len(_value) == 1:
				attrs[""] = _value[0]

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
			node = handleElement(self.node, defines=defines, slots=self.slots)[0]

			node.render_offset = self.render_offset
			node.render_boundary_left_top = self.render_boundary_left_top
			node.render_boundary_right_bottom = self.render_boundary_right_bottom
			node.parent = self.parent
			node.render_stretch = self.render_stretch

			return node.render(*args, **kwargs)

	return FromXml