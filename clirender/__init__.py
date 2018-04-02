from screen import *
from layout import *

def easyRender(xml):
	from layout.xml_parser import gatherLibs, fromXml
	from layout.libs import getAdditionalNodes, render

	libs = gatherLibs(xml)
	nodes = getAdditionalNodes(libs)
	root = fromXml(xml, additional_nodes=nodes)

	layout = Layout(root)
	render(layout, libs)
	return layout