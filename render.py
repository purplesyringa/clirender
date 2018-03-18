#!/usr/bin/env python
import sys
from clirender.layout import xml_parser, Layout
from clirender.layout.libs import render

with open(sys.argv[1]) as f:
	xml = f.read()

libs = xml_parser.gatherLibs(xml)
root = xml_parser.fromXml(xml, additional_nodes={})

layout = Layout(root)
render(layout, libs)