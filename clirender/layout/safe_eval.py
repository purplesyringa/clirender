def safeEval(expr, scope):
	scope = dict(**scope)
	scope["__builtins__"] = None
	return eval(expr, scope)