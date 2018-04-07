from rect import Rect
from switch import Switch
from ..exceptions import NoStretchError
import operator

class StackPanel(Rect):
	container = True
	text_container = False
	properties = ["orientation", "hspacing", "wspacing", "optimize"]

	def init(self, width=None, height=None, orientation="horizontal", hspacing=0, wspacing=0, optimize="safe"):
		self.orientation = orientation
		self.hspacing = hspacing
		self.wspacing = wspacing
		self.optimize = optimize

		self._render_cache = None

		return dict(width=width, height=height)

	def onRender(self, dry_run=False):
		if self.optimize != "no":
			if not (self._completely_revoked or self._revoked) and self._render_cache:
				# Nothing was changed since last render
				return self.cache_sizes


		# Guess container size
		if self.orientation == "vertical":
			stretch = self.width
		else:
			stretch = self.height

		if self.width is None or self.height is None:
			# Let guessContainerSize() find out 'stretch' if it is not given
			width, height, stretch = self.guessContainerSize(stretch=stretch)
			if self.width is not None:
				width = self.width
			if self.height is not None:
				height = self.height
		else:
			# If the size is given, don't do unnecessary actions
			width, height = self.width, self.height

		width, height = self.render(StackPanel, dry_run=dry_run, width=width, height=height)
		self.renderChildren(width, height, dry_run=dry_run, stretch=stretch)

		if not dry_run:
			self._render_cache = self.render_offset
		return width, height

	def guessContainerSize(self, stretch=None):
		width, height = self.render(StackPanel, dry_run=True, width=self.width or 0, height=self.height or 0)

		return self.renderChildren(width, height, dry_run=True, stretch=stretch)

	def renderChildren(self, width, height, dry_run=False, stretch=None):
		x2, y2 = map(operator.add, self.render_offset, (width, height))

		if self._completely_revoked:
			# Position was changed
			rerender = True
		elif self._revoked and self.bg is not None:
			# If the size or the background of children was changed,
			# we need to rerender this StackPanel, too
			rerender = True
		elif self._revoked:
			# Nothing was changed on screen since last render, but
			# some child was changed
			rerender = False
		else:
			rerender = True

		if self.optimize == "no":
			rerender = True

		wspacing = self.layout.calcRelativeSize(self.wspacing, self.render_parent_width,  self.render_stretch)
		hspacing = self.layout.calcRelativeSize(self.hspacing, self.render_parent_height, self.render_stretch)

		x1, y1 = self.render_offset
		cur_x, cur_y = x1, y1
		max_width, max_height = 0, 0

		rows_columns = []

		row_column_has_stretch_problems = False
		rows_columns_no_stretch = []

		for child in self.children:
			if isinstance(child, Switch):
				# <Switch /> can be used to switch direction
				if self.orientation == "vertical":
					if not row_column_has_stretch_problems:
						rows_columns_no_stretch.append(cur_y - y1)

					rows_columns.append((max_width, cur_y - y1))

					cur_x += max_width + wspacing
					cur_y = y1
				else:
					if not row_column_has_stretch_problems:
						rows_columns_no_stretch.append(cur_x - x1)

					rows_columns.append((cur_x - x1, max_height))

					cur_x = x1
					cur_y += max_height + hspacing

				max_width = 0
				max_height = 0

				row_column_has_stretch_problems = False
				continue

			boundary_left_top = self.render_boundary_left_top[:]
			boundary_left_top[0] = max(boundary_left_top[0], cur_x)
			boundary_left_top[1] = max(boundary_left_top[1], cur_y)

			boundary_right_bottom = self.render_boundary_right_bottom[:]
			if self.width is not None:
				boundary_right_bottom[0] = min(boundary_right_bottom[0], x2)
			if self.height is not None:
				boundary_right_bottom[1] = min(boundary_right_bottom[1], y2)

			if self.optimize == "aggressive":
				if rerender == "this":
					rerender = "maybe"
				if rerender == "maybe":
					if hasattr(child, "_render_cache"):
						# Maybe the position wasn't changed, and we don't have to
						# rerender completely?
						if child._render_cache != (cur_x, cur_y):
							rerender = "this"
				elif child._revoked and not self._completely_revoked:
					rerender = "maybe"

			try:
				child_width, child_height = self.renderChild(
					child, dry_run=dry_run,

					offset=(cur_x, cur_y),
					boundary_left_top=boundary_left_top,
					boundary_right_bottom=boundary_right_bottom,
					parent_width=x2 - x1,
					parent_height=y2 - y1,
					stretch = stretch,

					completely_revoked=(rerender is True or rerender == "this")
				)
			except NoStretchError:
				row_column_has_stretch_problems = True
				continue

			max_width = max(max_width, child_width)
			max_height = max(max_height, child_height)

			if self.orientation == "vertical":
				cur_y += child_height + hspacing
			else:
				cur_x += child_width + wspacing

		if len(rows_columns_no_stretch) < len(rows_columns):
			# Some rows/columns used 'stretch' variable, which was not calculated yet
			if self.orientation == "vertical":
				stretch = sum(rows_columns_no_stretch) + cur_y - y1
			else:
				stretch = sum(rows_columns_no_stretch) + cur_x - x1

			return self.renderChildren(width, height, dry_run=dry_run, stretch=stretch)

		if self.orientation == "vertical":
			rows_columns.append((max_width, cur_y - y1))
			return sum(value[0] for value in rows_columns), max(value[1] for value in rows_columns), stretch
		else:
			rows_columns.append((cur_x - x1, max_height))
			return max(value[0] for value in rows_columns), sum(value[1] for value in rows_columns), stretch