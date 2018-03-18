#!/usr/bin/env python
import sys
from clirender.layout import xml_parser, Layout
from clirender.layout.libs import render, getAdditionalNodes

with open(sys.argv[1]) as f:
	xml = f.read()

libs = xml_parser.gatherLibs(xml)
nodes = getAdditionalNodes(libs)
root = xml_parser.fromXml(xml, additional_nodes=nodes)

layout = Layout(root)
render(layout, libs)