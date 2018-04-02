from asteval import Interpreter

def safeEval(expr, scope):
	interpreter = Interpreter(
		usersyms=dict(**scope),
		use_numpy=False,
		minimal=False
	)

	res = interpreter.eval(expr, show_errors=False)

	if interpreter.error:
		raise interpreter.error

	return res