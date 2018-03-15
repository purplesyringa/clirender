def getLibInfo(lib):
	import all
	if not hasattr(all, lib):
		raise AttributeError("No %s lib" % lib)
	return getattr(all, lib)

def getDependencies(libs):
	res = []
	for lib in libs:
		dependencies = getattr(getLibInfo(lib), "dependencies", [])
		res += getDependencies(dependencies)
		res.append(lib)
	return res

def render(layout, libs):
	libs = getDependencies(libs)

	lib_instances = {}
	for lib in libs:
		lib_instances[lib] = getLibInfo(lib)(layout)

	layout.render()

	if any(hasattr(lib, "loop") for lib in lib_instances.values()):
		while True:
			for lib in lib_instances.values():
				if hasattr(lib, "beforeLoop"):
					lib.beforeLoop(lib_instances)
			for lib in lib_instances.values():
				if hasattr(lib, "loop"):
					lib.loop(lib_instances)

			layout.render()