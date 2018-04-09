from screen import *
from layout import *
from layout.libs import register
from layout.api import createLayoutAPI

def easyRender(xml):
	from layout.xml_parser import gatherLibs, fromXml
	from layout.libs import getAdditionalNodes, getAdditionalSlots, render

	libs = gatherLibs(xml)
	nodes = getAdditionalNodes(libs)
	slots = getAdditionalSlots(libs)

	layout = Layout()
	slots["layout"] = createLayoutAPI(layout)
	root = fromXml(xml, additional_nodes=nodes, global_slots=slots)
	layout.bind(root)

	render(layout, libs)
	return layout