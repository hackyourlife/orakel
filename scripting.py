# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import ast
import operator as op
import math
from urllib.parse import quote as urlencode

"""
import sys

module = dir(sys.modules[__name__])
for attr in (a for a in dir(module) if not a.startswith('_')):
	func = getattr(module, attr)
"""

import datetime
import uuid as guid

_ISO8601_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
_DATE_FORMAT = '%d.%m.%Y'
_TIME_FORMAT = '%H:%M:%S'


def uuid():
	return str(guid.uuid4())

def isotime(at=None):
	"""Stringify time in ISO 8601 format."""
	if not at:
		at = utcnow()
	st = at.strftime(_ISO8601_TIME_FORMAT)
	tz = at.tzinfo.tzname(None) if at.tzinfo else 'UTC'
	st += ('Z' if tz == 'UTC' else tz)
	return st

def date(at=None):
	if not at:
		at = now()
	st = at.strftime(_DATE_FORMAT)
	return st

def time(at=None):
	if not at:
		at = now()
	st = at.strftime(_TIME_FORMAT)
	return st

def utcnow():
	return datetime.datetime.utcnow()

def now():
	return datetime.datetime.now()

def ping(ip):
	return "not implemented"

search_engines = { 'google': 'https://www.google.com/search?q=%s' }
def search(engine, query):
	return search_engines[engine] % urlencode(query)

class ReturnException(Exception):
	def __init__(self, value):
		Exception.__init__(self)
		self.value = value

class Scripting(object):
	# supported operators
	operators = {	ast.Add: op.add,
			ast.Sub: op.sub,
			ast.Mult: op.mul,
			ast.Div: op.truediv,
			ast.Pow: op.pow,
			ast.BitXor: op.xor }

	constants = {	"pi": math.pi,
			"π": math.pi,
			"True": True,
			"False": False }

	functions  = {	"sin": math.sin,
			"cos": math.cos,
			"tan": math.tan,
			"asin": math.asin,
			"acos": math.acos,
			"atan": math.atan,
			"log": math.log,
			"exp": math.exp,
			"now": now,
			"utc": utcnow,
			"date": date,
			"time": time,
			"uuid": uuid,
			"search": search
	}

	def __init__(self, storage):
		self.storage = storage
		try:
			self.variables = storage["variables"]
		except:
			self.variables = {}

	def evaluate(self, expr):
		x = ast.parse(expr)
		try:
			result = [ self._eval(z) for z in x.body ]
		except ReturnException as e:
			self.storage["variables"] = self.variables
			return e.value
		except:
			raise
		self.storage["variables"] = self.variables
		return result[-1]

	def _eval(self, node):
		if isinstance(node, ast.Num):
			return node.n
		elif isinstance(node, ast.Str):
			return node.s
		elif isinstance(node, ast.Expr):
			return self._eval(node.value)
		elif isinstance(node, ast.Return):
			raise ReturnException(self._eval(node.value))
		elif isinstance(node, ast.Attribute):
			raise NotImplemented
		elif isinstance(node, ast.Call):
			if isinstance(node.func, ast.Attribute):
				raise NotImplemented
			function = node.func.id
			args = [ self._eval(x) for x in node.args ]
			return self.functions[function](*args)
		elif isinstance(node, ast.Name):
			if node.id in self.constants:
				return self.constants[node.id]
			else:
				return self.variables[node.id]
		elif isinstance(node, ast.operator): # <operator>
			return self.operators[type(node)]
		elif isinstance(node, ast.BinOp): # <left> <operator> <right>
			operator = self._eval(node.op)
			if operator is op.pow:
				right = self._eval(node.right)
				if right > 200:
					raise Exception('pow')
			return self._eval(node.op)(self._eval(node.left),
					self._eval(node.right))
		elif isinstance(node, ast.Assign):
			target = node.targets[0].id
			value = self._eval(node.value)
			if target in self.constants:
				raise SyntaxError('cannot assign to constant')
			self.variables[target] = value
			#return value
			return None
		else:
			raise TypeError(node)

	def __call__(self, msg, nick, send_message):
		try:
			result = self.evaluate(msg)
			if result:
				send_message(str(result))
				return True
		except:
			pass
		return False

if __name__ == "__main__":
	code = """
return "Hello, World"
	"""
	s = Scripting()
	print("result: '%s'" % s.evaluate(code))
