#!/usr/bin/env python
import sys
from clirender import easyRender

with open(sys.argv[1]) as f:
	xml = f.read()

easyRender(xml)