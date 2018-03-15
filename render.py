#!/usr/bin/env python
import sys
from clirender.layout import xml_parser, Layout

with open(sys.argv[1]) as f:
	xml = f.read()

root, libs = xml_parser.fromXml(xml)

layout = Layout(root)
layout.render()
print libs