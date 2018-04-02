from asteval import Interpreter

def safeEval(expr, scope):
	scope = dict(**scope)
	for name in scope:
		if getattr(scope[name], "wrapped", False) is True:
			scope[name] = scope[name](scope)

	interpreter = Interpreter(
		usersyms=scope,
		use_numpy=False,
		minimal=False
	)

	res = interpreter.eval(expr, show_errors=False)

	if interpreter.error:
		raise interpreter.error

	return res