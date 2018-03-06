from layout import Layout
from layout.rect import Rect
from layout.stackpanel import StackPanel

layout = Layout(
	StackPanel(
		width="100%", height="100%",
		vertical=False,

		children=[
			Rect(
				width="20%", height="100%",
				bg="#232A31 | white"
			),
			Rect(
				width="80%", height="100%",
				bg="black"
			)
		]
	)
)
layout.render()