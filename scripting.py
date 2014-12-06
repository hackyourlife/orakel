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
from utils import oneof, load_database
from module import Module, MUC, CONFIG, COMMAND

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
	resolver.lifetime = 5
	result = [ str(x) for x in resolver.query(domain, record) ]
	return result

class ReturnException(Exception):
	def __init__(self, value):
		Exception.__init__(self)
		self.value = value

class TimeoutException(Exception):
	pass

def signal_handler(signum, frame):
	raise TimeoutException()
signal.signal(signal.SIGALRM, signal_handler)

@contextmanager
def time_limit(seconds):
	def signal_handler(signum, frame):
		raise TimeoutException()
	signal.signal(signal.SIGALRM, signal_handler)
	signal.alarm(seconds)
	try:
		yield
	finally:
		signal.alarm(0)

@contextmanager
def __time_limit(seconds):
	signal.alarm(seconds)
	try:
		yield
	finally:
		signal.alarm(0)

class Scripting(Module):
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
			"isotime" : isotime,
			"uuid": uuid,
			"ping": ping,
			"alive": alive,
			"dnsquery": dnsquery,
			"random": random.random,
			"randrange": random.randrange,
			"oneof": oneof
	}

	def __init__(self, search_engine_file=None, **keywords):
		super(Scripting, self).__init__([MUC, CONFIG, COMMAND],
				name=__name__, **keywords)

		self.search_engine_file = search_engine_file
		self.variables = {}

		functions = {
			"search": self.search,
			"vars": self._vars,
			"eval": self.do_eval }
		for key in functions.keys():
			self.functions[key] = functions[key]

		self.send_cmd("get_config", key="variables", default={})
		self.reload_config()

	def reload_config(self):
		self.search_engines = load_database(self.search_engine_file)

	def command(self, cmd, **keywords):
		if cmd == "config_value":
			if keywords["key"] == "variables":
				self.variables = keywords["value"]
		elif cmd == "config_values":
			self.variables = keywords["value"]["variables"]

	def evaluate(self, expr):
		x = ast.parse(expr)
		try:
			result = [ self._eval(z) for z in x.body ]
		except ReturnException as e:
			self.send_cfg("variables", self.variables)
			return e.value
		except:
			raise
		self.send_cfg("variables", self.variables)
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
		elif isinstance(node, ast.Tuple):
			return tuple([ self._eval(x) for x in node.elts ])
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
		elif isinstance(node, ast.Compare):
			print(vars(node))
			left = self._eval(node.left)
			value = True
			for i in range(len(node.ops)):
				right = self._eval(node.comparators[i])
				value = value and (self.compare(left,
					node.ops[i], right))
				left = right
			return value
		else:
			raise TypeError(node)

	def compare(self, left, op, right):
		if isinstance(op, ast.Eq):
			return left == right
		elif isinstance(op, ast.NotEq):
			return left != right
		elif isinstance(op, ast.Lt):
			return left < right
		elif isinstance(op, ast.LtE):
			return left <= right
		elif isinstance(op, ast.Gt):
			return left > right
		elif isinstance(op, ast.GtE):
			return left >= right
		elif isinstance(op, ast.Is):
			return left is right
		elif isinstance(op, ast.IsNot):
			return not left is right
		elif isinstance(op, ast.In):
			return left in right
		elif isinstance(op, ast.NotIn):
			return not left in right
		raise TypeError(op)

	def muc_msg(self, msg, nick, jid, role, affiliation, **keywords):
		self.constants['__nick__'] = nick
		self.constants['__jid__'] = jid
		self.constants['__role__'] = role
		self.constants['__affiliation__'] = affiliation
		def allowed(c):
			if c in ["\r", "\n", "\t"]:
				return True
			if ord(c) < 32:
				return False
			return True
		if re.match(r'^\s*[a-zA-Z0-9]+[\.\s]*$', msg):
			return
		if re.match(r'^\s*[0-9]+\.[0-9]+\s*$', msg):
			return
		try:
			if msg in self.variables:
				return
			with time_limit(10):
				result = self.evaluate(msg)
			if not result is None:
				if ("'%s'" % str(result)) == msg or \
						('"%s"' % str(result)) == \
							msg or \
						("'%s'" % str(result)) == \
							msg.strip() or \
						('"%s"' % str(result)) == \
							msg.strip():
					return
				result = [ c for c in str(result)
						if allowed(c) ]
				if len(result) > 750:
					result = result[:750] + ["…"]
				self.send_muc("".join(result))
		except SyntaxError:
			pass
		except dns.resolver.NXDOMAIN:
			self.send_muc('Exception: NXDOMAIN')
		except dns.exception.Timeout:
			self.send_muc('Exception: timeout')
		except:
			#traceback.print_exc()
			pass
