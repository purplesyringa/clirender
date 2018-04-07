import inspect # magic

class Element(object):
	def __init__(self):
		pass


	def init(self):
		pass

	def runInit(self, **kwargs):
		mro = type(self).__mro__

		for basecls in mro:
			if not issubclass(basecls, Element):
				continue
			elif "init" not in basecls.__dict__:
				continue

			init = basecls.__dict__["init"]

			args = inspect.getargspec(init)
			if args.varargs is not None:
				raise ValueError("%s.init() method accepts *%s" % (basecls.__name__, arg.varargs))

			# Check that all needed arguments exist
			cnt = len(args.args) - len(args.defaults or [])
			need_args = args.args[1:cnt - 1] # Remove self
			for name in need_args:
				if name not in kwargs:
					raise ValueError("Expected attribute %s for %s" % (name, basecls.__name__))

			# Check that we don't pass something we don't have to
			local_kwargs = {}
			for name, value in kwargs.items():
				if args.keywords is not None or name in args.args:
					local_kwargs[name] = value
					del kwargs[name]


			bound = init.__get__(self, basecls)
			changed = bound(**local_kwargs)
			if changed is not None:
				kwargs.update(changed)


		if len(kwargs) > 0:
			raise ValueError("Unexpected attribute %s" % name)