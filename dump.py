#!/usr/bin/env python
import sys
from clirender.layout import dump, xml_parser

with open(sys.argv[1]) as f:
	xml = f.read()

root = xml_parser.fromXml(xml)
dump(root)