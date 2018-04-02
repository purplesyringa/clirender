from screen import *
from layout import *
from layout.libs import register

def easyRender(xml):
	from layout.xml_parser import gatherLibs, fromXml
	from layout.libs import getAdditionalNodes, getAdditionalSlots, render

	libs = gatherLibs(xml)
	nodes = getAdditionalNodes(libs)
	slots = getAdditionalSlots(libs)
	root = fromXml(xml, additional_nodes=nodes, global_slots=slots)

	layout = Layout(root)
	render(layout, libs)
	return layout