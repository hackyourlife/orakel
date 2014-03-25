# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import ast
import operator as op
import math
import re
from urllib.parse import quote as urlencode
import dns.resolver
import icmplib
import random
import traceback
import signal
from contextlib import contextmanager

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

def ping(address):
	return icmplib.ping(address)

def alive(address):
	try:
		if icmplib.ping(address):
			return "%s is alive!" % address
	except:
		pass
	return "%s is dead!" % address

def dnsquery(domain, record='A'):
	records = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'PTR', 'SOA', 'SRV', 'TXT']
	if not record in records:
		raise Exception('permission denied')
	resolver = dns.resolver.Resolver()
	resolver.nameservers = [ '8.8.8.8', '8.8.4.4' ]
	result = [ str(x) for x in resolver.query(domain, record) ]
	return result

class ReturnException(Exception):
	def __init__(self, value):
		Exception.__init__(self)
		self.value = value

class TimeoutException(Exception):
	pass

@contextmanager
def __time_limit(seconds):
	def signal_handler(signum, frame):
		raise TimeoutException()
	signal.signal(signal.SIGALRM, signal_handler)
	signal.alarm(seconds)
	try:
		yield
	finally:
		signal.alarm(0)

def signal_handler(signum, frame):
	raise TimeoutException()
signal.signal(signal.SIGALRM, signal_handler)

@contextmanager
def time_limit(seconds):
	signal.alarm(seconds)
	try:
		yield
	finally:
		signal.alarm(0)

class Scripting(object):
	# supported operators
	operators = {	ast.Add: op.add,
			ast.Sub: op.sub,
			ast.Mult: op.mul,
			ast.Div: op.truediv,
			ast.Pow: op.pow,
			ast.BitXor: op.xor,
			ast.BitOr: op.or_,
			ast.BitAnd: op.and_,
			ast.Mod: op.mod }

	unaryoperators = {
			ast.USub: op.neg,
			ast.UAdd: op.pos,
			ast.Invert: op.invert }

	attrfunctions = {
			ast.Str: {
				"capitalize": str.capitalize,
				"index": str.index,
				"isalnum": str.isalnum,
				"isalpha": str.isalpha,
				"isdigit": str.isdigit,
				"islower": str.islower,
				"isspace": str.isspace,
				"istitle": str.istitle,
				"isupper": str.isupper,
				"join": str.join,
				"lower": str.lower,
				"replace": str.replace,
				"split": str.split,
				"splitlines": str.splitlines,
				"startswith": str.startswith,
				"strip": str.strip,
				"swapcase": str.swapcase,
				"title": str.title,
				"upper": str.upper,
				"zfill": str.zfill } }

	constants = {	"pi": math.pi,
			"π": math.pi,
			"True": True,
			"False": False,
			"None": None }

	def search(self, engine, query):
		return self.search_engines[engine] % urlencode(query)

	def _vars(self):
		return self.variables

	def do_eval(self, expression):
		return self.evaluate(expression)

	functions  = {	"sin": math.sin,
			"cos": math.cos,
			"tan": math.tan,
			"asin": math.asin,
			"acos": math.acos,
			"atan": math.atan,
			"log": math.log,
			"exp": math.exp,
			"sqrt": math.sqrt,
			"abs": abs,
			"all": all,
			"any": any,
			"bin": bin,
			"bool": bool,
			"chr": chr,
			"complex": complex,
			"dict": dict,
			"float": float,
			"hex": hex,
			"int": int,
			"len": len,
			"list": list,
			"max": max,
			"min": min,
			"oct": oct,
			"ord": ord,
			"range": range,
			"str": str,
			"sum": sum,
			"tuple": tuple,
			"type": type,
			"now": now,
			"utc": utcnow,
			"date": date,
			"time": time,
			"uuid": uuid,
			"ping": ping,
			"alive": alive,
			"dnsquery": dnsquery,
			"random": random.random,
			"randrange": random.randrange,
	}

	def __init__(self, storage=None, search_engines={}):
		self.storage = storage
		self.search_engines = search_engines
		try:
			self.variables = storage["variables"]
		except:
			self.variables = {}

		functions = {
			"search": self.search,
			"vars": self._vars,
			"eval": self.do_eval }
		for key in functions.keys():
			self.functions[key] = functions[key]

	def evaluate(self, expr):
		x = ast.parse(expr)
		try:
			result = [ self._eval(z) for z in x.body ]
		except ReturnException as e:
			if not self.storage is None:
				self.storage["variables"] = self.variables
			return e.value
		except:
			raise
		if not self.storage is None:
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
		elif isinstance(node, ast.List):
			return [ self._eval(x) for x in node.elts ]
		elif isinstance(node, ast.Subscript):
			if isinstance(node.value, ast.Name):
				target = self.variables[node.value.id]
			else:
				target = self._eval(node.value)
			if isinstance(node.slice, ast.Index):
				value = self._eval(node.slice.value)
				return target[value]
			else:
				lower = self._eval(node.slice.lower)
				upper = self._eval(node.slice.upper)
				step = self._eval(node.slice.step)
				return target[lower:upper:step]
		elif isinstance(node, ast.ListComp):
			generator = node.generators[0]
			target = generator.target.id
			items = self._eval(generator.iter)
			if len(items) > 100:
				raise Exception('too many iterations')
			def step(x, y, z):
				self.variables[y] = z
				result = self._eval(x)
				del self.variables[y]
				return result
			return [ step(node.elt, target, x) for x in items ]
		elif isinstance(node, ast.Call):
			args = [ self._eval(x) for x in node.args ]
			if isinstance(node.func, ast.Attribute):
				obj = node.func.value
				func = node.func.attr
				if type(obj) in self.attrfunctions:
					function = self.attrfunctions[type(obj)][func]
				else:
					raise NotImplemented
				args = [ self._eval(node.func.value) ] + args
			else:
				function = self.functions[node.func.id]
			return function(*args)
		elif isinstance(node, ast.Name):
			if node.id in self.constants:
				return self.constants[node.id]
			else:
				return self.variables[node.id]
		elif isinstance(node, ast.operator): # <operator>
			return self.operators[type(node)]
		elif isinstance(node, ast.unaryop):
			return self.unaryoperators[type(node)]
		elif isinstance(node, ast.UnaryOp):
			return self._eval(node.op)(self._eval(node.operand))
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
		elif isinstance(node, ast.Delete):
			target = node.targets[0].id
			del self.variables[target]
		elif node is None:
			return None
		elif isinstance(node, int) or isinstance(node, str) \
				or isinstance(node, float) \
				or isinstance(node, list) \
				or isinstance(node, dict):
			return node
		else:
			raise TypeError(node)

	def __call__(self, msg, nick, send_message):
		def allowed(c):
			if c in ["\r", "\n", "\t"]:
				return True
			if ord(c) < 32:
				return False
			return True
		if re.match(r'^\s*[a-zA-Z0-9]+\s*$', msg):
			return False
		try:
			if msg in self.variables:
				return False
			with time_limit(10):
				result = self.evaluate(msg)
			if result:
				if ("'%s'" % result) == msg or \
						('"%s"' % result) == msg:
					return False
				result = [ c for c in str(result)
						if allowed(c) ]
				if len(result) > 500:
					result = result[:500] + "…"
				send_message("".join(result))
				return True
		except SyntaxError:
			pass
		except:
			print("%s: '%s'" % (nick, msg))
			traceback.print_exc()
		return False
