class Slot(object):
	def __init__(self, name, context):
		self.name = name
		self.context = context

	def evaluate(self):
		value = self.context.slot_context[self.name]
		if isinstance(value, Slot):
			return value.evaluate()
		return value

	def __str__(self):
		return ":%s" % self.name