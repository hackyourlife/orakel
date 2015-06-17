#!/bin/python
# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

WHITESPACE = [' ', '\r', '\n', '\t']

class Identifier(object):
	def __init__(self, name):
		self.name = name
	def __call__(self):
		return self.name
	def __str__(self):
		return self.name
	def __repr__(self):
		return self.name

class Function(object):
	def __init__(self, name, args, code):
		self.name = name
		self.args = args
		self.code = code
	def __str__(self):
		def fmt(x, top=True):
			if type(x) == str:
				return '"%s"' % x
			if type(x) == list:
				if top:
					return " ".join([ fmt(c, False) for c in x ])
				return "(%s)" % " ".join([ fmt(c, False) for c in x ])
			return str(x)
		prefix = "defun %s" % self.name if not self.name is None \
				else "lambda"
		return "(%s (%s) %s)" % (prefix, \
				" ".join([ str(a) for a in self.args]),
				fmt(self.code))
	def __repr__(self):
		return self.__str__()

class Context(object):
	def __init__(self, parent={}):
		self.parent = parent
		self.overlay = {}
	def __getitem__(self, key):
		if key in self.overlay:
			return self.overlay[key]
		return self.parent[key]
	def __setitem__(self, key, value):
		self.parent[key] = value
	def __contains__(self, key):
		return key in self.overlay or key in self.parent
	def __iter__(self):
		merged = self.concat()
		return merged.__iter__()
	def set(self, key, value):
		self.overlay[key] = value
	def concat(self):
		v = { key: self.parent[key] for key in self.parent }
		for key in self.overlay:
			v[key] = self.overlay[key]
		return v
	def __str__(self):
		return str(self.concat())
	def __repr__(self):
		return self.__str__()

def parse(text):
	ast = []
	i = 0
	l = len(text)

	def is_float(x):
		try:
			float(x)
			return True
		except ValueError:
			return False

	def is_integer(x):
		try:
			int(x)
			return True
		except ValueError:
			return False

	def parse_lisp_internal(text):
		global WHITESPACE

		v = []
		isstr = False
		bol = True
		escape = False
		l = len(text)
		txt = []

		def append():
			nonlocal v, txt
			if len(txt) > 0:
				t = "".join(txt)
				if is_integer(t):
					v += [ int(t) ]
				elif is_float(t):
					v += [ float(t) ]
				else:
					v += [ Identifier(t) ]
				txt = []

		i = 0
		while True:
			c = text[i]
			if bol:
				if c == '(':
					bol = False
			elif isstr:
				if c == '\\':
					escape = True
				elif (c == '"') and (not escape):
					isstr = False
					v += [ "".join(txt) ]
					txt = []
				else:
					escape = False
					txt += [ c ]
			elif c in WHITESPACE:
				append()
			elif c == '"':
				isstr = True
			elif c == '(':
				append()
				z, d = parse_lisp_internal(text[i:])
				v += [ z ]
				i += d
			elif c == ')':
				append()
				return v, i
			else:
				txt += [ c ]

			i += 1
			if i >= l:
				append()
				return v, l

	while True:
		code = text[i:]
		if not '(' in code: # no more expressions
			return ast

		tree, end = parse_lisp_internal(code)
		ast += [ tree ]
		i += end + 1
		if i >= l:
			return ast

def do_add(context, *args):
	return sum(lisp_eval(context, x) for x in args)

def do_sub(context, a, b):
	a = lisp_eval(context, a)
	b = lisp_eval(context, b)
	return a - b

def do_mul(context, *args):
	p = 1
	for arg in args:
		p *= lisp_eval(context, arg)
	return p

def do_div(context, a, b):
	a = lisp_eval(context, a)
	b = lisp_eval(context, b)
	return a / b

def do_inc(context, x):
	return lisp_eval(context, x) + 1

def do_dec(context, x):
	return lisp_eval(context, x) - 1

def do_lt(context, a, b):
	a = lisp_eval(context, a)
	b = lisp_eval(context, b)
	return a < b

def do_gt(context, a, b):
	a = lisp_eval(context, a)
	b = lisp_eval(context, b)
	return a > b

def do_le(context, a, b):
	a = lisp_eval(context, a)
	b = lisp_eval(context, b)
	return a <= b

def do_ge(context, a, b):
	a = lisp_eval(context, a)
	b = lisp_eval(context, b)
	return a >= b

def do_eq(context, a, b):
	a = lisp_eval(context, a)
	b = lisp_eval(context, b)
	return a == b

def do_not(context, x):
	return not lisp_eval(context, x)

def do_and(context, a, b):
	a = lisp_eval(context, a)
	b = lisp_eval(context, b)
	return a and b

def do_or(context, a, b):
	a = lisp_eval(context, a)
	b = lisp_eval(context, b)
	return a or b

def do_if(context, test, when, otherwise):
	c = lisp_eval(context, test)
	if c:
		return lisp_eval(context, when)
	else:
		return lisp_eval(context, otherwise)

def do_when(context, test, when):
	c = lisp_eval(context, test)
	if c:
		return lisp_eval(context, when)
	return None

def do_let(context, variables, *methods):
	ctx = Context(context)
	overlay = {}
	for var in variables:
		if type(var) != list:
			raise SyntaxError("can only process lists")
		if len(var) != 2:
			raise SyntaxError("exactly two token required")
		if type(var[0]) != Identifier:
			raise SyntaxError("identifier expected")
		overlay[var[0].name] = lisp_eval(ctx, var[1])
	ctx.overlay = overlay
	return lisp_run(ctx, methods)

def do_defun(context, name, args, *content):
	if type(name) != Identifier:
		raise SyntaxError("identifier expected")
	context[name.name] = Function(name, args, list(content))

def do_defconstant(context, name, value):
	if type(name) != Identifier:
		raise SyntaxError("identifier expected")
	context[name.name] = lisp_eval(context, value)

def do_set(context, name, value):
	context[name] = lisp_eval(context, value)

def do_lambda(context, args, *content):
	return Function(None, args, list(content))

def do_funcall(context, function, *args):
	function = lisp_eval(context, function)
	a = [ lisp_eval(context, x) for x in args ]
	return lisp_run_function(context, function, *a)

def do_list(context, *value):
	return lisp_eval(context, values)

def do_progn(context, *expressions):
	r = None
	for expression in expressions:
		r = lisp_eval(context, expression)
	return r

def do_substr(context, string, start, stop=None):
	s = lisp_eval(context, string)
	if stop == None:
		return s[start:]
	return s[start:stop]

def do_getidx(context, string, index):
	s = lisp_eval(context, string)
	i = lisp_eval(context, index)
	return s[i]

def do_print(context, *args):
	print(*[ lisp_eval(context, arg) for arg in args ])

def do_printf(context, *args):
	if len(args) > 1:
		values = [ lisp_eval(context, arg) for arg in args ]
		print(values[0] % tuple(values[1:]))
	else:
		print(*args)

def lisp_replace_variables(code, context):
	#print("REPLACE[%s]" % (str(code)))
	def replace(x):
		if type(x) == Identifier and x.name in context:
			return context[x.name]
		if type(x) == list:
			return lisp_replace_variables(x, context)
		return x
	if type(code) == list or type(code) == tuple:
		return [ replace(x) for x in code ]
	return replace(code)

def lisp_run_function(context, function, *args):
	signature = function.args
	replacements = { signature[i].name: lisp_eval(context, args[i]) \
			for i in range(len(signature)) }
	code = lisp_replace_variables(function.code, replacements)
	return lisp_run(context, code)

methods = {
		'+':		do_add,
		'-':		do_sub,
		'*':		do_mul,
		'/':		do_div,
		'1+':		do_inc,
		'1-':		do_dec,
		'<':		do_lt,
		'>':		do_gt,
		'=':		do_eq,
		'<=':		do_le,
		'>=':		do_ge,
		'not':		do_not,
		'and':		do_and,
		'or':		do_or,
		'&':		do_and,
		'|':		do_or,
		'if':		do_if,
		'when':		do_when,
		'let':		do_let,
		'defun':	do_defun,
		'defconstant':	do_defconstant,
		'set':		do_set,
		'lambda':	do_lambda,
		'funcall':	do_funcall,
		'list':		do_list,
		'progn':	do_progn,
		'substr':	do_substr,
		'getidx':	do_getidx,
		'print':	do_print,
		'printf':	do_printf
}

default_variables = {
		'true':		True,
		'false':	False,
		'nil':		None
}

def create_default_context():
	global default_variables
	return Context({ key: default_variables[key] \
			for key in default_variables })

def lisp_call(context, method, *args):
	global methods
	if method in context:
		return lisp_run_function(context, context[method], *args)
	elif method in methods:
		return methods[method](context, *args)
	raise NameError("undefined method '%s'" % method)

def lisp_run_expr(context, expression):
	#print("EXEC[%s]" % expression)
	if type(expression) != list:
		raise SyntaxError("can only execute list")
	if len(expression) < 1:
		raise SyntaxError("non empty list expected")
	if type(expression[0]) != Identifier:
		raise SyntaxError("identifier expected")
	method = expression[0].name
	args = [ context, method ]
	if len(expression) > 1:
		args += expression[1:]
	return lisp_call(*args)

def lisp_eval(context, expression):
	if type(expression) == list:
		return lisp_run_expr(context, expression)
	elif type(expression) == int or type(expression) == float \
			or type(expression) == str:
		return expression
	elif type(expression) == Identifier:
		return context[expression.name]
	raise SyntaxError("unexpected token type")

def lisp_run(context, ast):
	rv = None
	for expression in ast:
		rv = lisp_run_expr(context, expression)
	return rv

execute = lisp_run

if __name__ == "__main__":
	context = create_default_context()
	code = r"""
(print "hello, world")
(defun f (x) (printf "hi %s" x))
(defun wtf () (print "wtf?!"))
(wtf)
(f "tester")
(printf "Value: %s" (+ 1 2 0.5))
(printf "%d" (1+ 5))
(let ((x 7) (y 8)) (printf "x = %d" x) (printf "y = %d" y))
(defconstant +year-size+ 365)
 
 (defun birthday-paradox (probability number-of-people)
   (let ((new-probability (* (/ (- +year-size+ number-of-people)
                                  +year-size+)
                              probability)))
      (if (< new-probability 0.5)
          (1+ number-of-people)
          (birthday-paradox new-probability (1+ number-of-people)))))

(printf "birthday-paradox = %s" (birthday-paradox 1.0 1))

(printf "progn = %s" (progn (print "hello, world") (print "it works") 5 (+ 1 2)))
(printf "%s" (lambda (x y) (+ x y)))
(funcall (lambda (x y) (printf "%d + %d = %d" x y (+ x y))) 2 3)
(printf "%d" (funcall (lambda (x y) (* x y) (+ x y)) 2 3))
(printf "[3] = '%c'" (getidx "hello" 3))
(printf "a \"quote\"")
	"""

	ast = lisp_parse(code)
	lisp_run(context, ast)
