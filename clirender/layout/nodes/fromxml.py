from node import Node

class NoDefault(object):
	pass

def fromXml(elem, slots, name, defines, container, additional_nodes):
	class FromXml(Node):
		def __new__(cls, **attrs):
			if cls.text_container:
				attrs[""] = attrs["value"]
				del attrs["value"]
			elif cls.container:
				if len(attrs["children"]) > 1:
					raise ValueError("Too many nodes in <%s>" % name)
				elif len(attrs["children"]) == 1:
					attrs[""] = attrs["children"][0]
					del attrs["children"]
				else:
					raise ValueError("Too less nodes in <%s>" % name)


			cur_slots = dict(**slots)
			for attr, value in attrs.items():
				if attr not in cur_slots and attr != "":
					raise ValueError("Unexpected slot :%s" % attr)

				cur_slots[attr] = value

			for slot in cur_slots.values():
				if isinstance(slot, NoDefault):
					raise ValueError("Required slot :%s not passed" % slot)

			from ..xml_parser import handleElement
			items = handleElement(elem, defines=defines, slots=cur_slots, additional_nodes=additional_nodes)
			if len(items) != 1:
				raise ValueError("<Define> must contain exactly one node")
			return items[0]

	FromXml.text_container = container == "text"
	FromXml.container = container == "node"

	return FromXml