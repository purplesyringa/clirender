#!/usr/bin/env python

from layout import xml_parser
from layout import Layout

root = xml_parser.fromXml("""
	<StackPanel width="100%" height="100%" vertical="False">
		<Rect width="20%" height="100%" bg="#232A31 | white" />
		<Rect width="80%" height="100%" bg="black" />
	</StackPanel>
""")

layout = Layout(root)
layout.render()