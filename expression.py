#!/bin/python
# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import ast
import operator as op
import math

# supported operators
operators = { ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
		ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor }

functions = { 'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
		'log': math.log, 'sqrt': math.sqrt }

constants = { 'pi': math.pi, 'π': math.pi, 'e': math.exp(1) }

def eval_expr(expr):
	"""
	>>> eval_expr('2^6')
	4
	>>> eval_expr('2**6')
	64
	>>> eval_expr('1 + 2*3**(4^5) / (6 + -7)')
	-5.0
	"""
	if(len(expr) > 64):
		raise Exception('size')
	return _eval(ast.parse(expr).body[0].value)

def _eval(node):
	if isinstance(node, ast.Num): # <number>
		return node.n
	elif isinstance(node, ast.Name):
		return constants[node.id]
	elif isinstance(node, ast.operator): # <operator>
		return operators[type(node)]
	elif isinstance(node, ast.Call): # <operator>()
		if len(node.args) != 1:
			raise TypeError(node.args)
		func = functions[node.func.id]
		value = _eval(node.args[0])
		return func(value)
	elif isinstance(node, ast.BinOp): # <left> <operator> <right>
		operator = _eval(node.op)
		if operator is op.pow:
			right = _eval(node.right)
			if right > 200:
				raise Exception('pow')
		return _eval(node.op)(_eval(node.left), _eval(node.right))
	else:
		raise TypeError(node)

class Expression(object):
	def __call__(self, msg, nick, send_message):
		try:
			result = eval_expr(msg)
			send_message(str(result))
			return True
		except:
			return False
