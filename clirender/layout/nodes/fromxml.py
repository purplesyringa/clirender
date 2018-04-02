from generator import Generator

class NoDefault(object):
	pass

def fromXml(elem, slots, name, defines, container, additional_nodes, global_slots):
	class FromXml(Generator):
		def __new__(cls, **attrs):
			from ..xml_parser import handleElement

			if cls.text_container:
				attrs[""] = attrs["value"]
				del attrs["value"]
			elif cls.container:
				if len(attrs["children"]) > 1:
					raise ValueError("Too many nodes in <%s>" % name)
				elif len(attrs["children"]) == 1:
					rendered = handleElement(attrs["children"][0], defines=defines, slots=attrs["slots"], additional_nodes=additional_nodes, global_slots=global_slots)
					if len(rendered) != 1:
						raise ValueError("Rendered <Slot /> must contain exactly one node")

					attrs[""] = rendered[0]
					del attrs["children"]
				else:
					raise ValueError("Too less nodes in <%s>" % name)

			del attrs["slots"]

			cur_slots = dict(**slots)
			for attr, value in attrs.items():
				if attr not in cur_slots and attr != "":
					raise ValueError("Unexpected slot :%s" % attr)

				cur_slots[attr] = value

			for slot in cur_slots.values():
				if isinstance(slot, NoDefault):
					raise ValueError("Required slot :%s not passed" % slot)

			items = handleElement(elem, defines=defines, slots=cur_slots, additional_nodes=additional_nodes, global_slots=global_slots)
			if len(items) != 1:
				raise ValueError("<Define> must contain exactly one node")
			return items[0]

	FromXml.text_container = container == "text"
	FromXml.container = container == "node"

	return FromXml