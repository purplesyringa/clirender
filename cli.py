from layout import Layout
from layout.rect import Rect
from layout.stackpanel import StackPanel

layout = Layout(
	StackPanel(
		width=20, height=20,
		bg="red",
		vertical=False,

		children=[
			Rect(
				width=5, height=3,
				bg="yellow"
			),
			Rect(
				width=3, height=5,
				bg="green"
			)
		]
	)
)
layout.render()