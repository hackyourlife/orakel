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
from lisp import parse as lisp_parse, execute as lisp_execute, \
		create_default_context, set_print_function
from contextlib import contextmanager
from utils import oneof, load_database
from module import Module, PRESENCE, MUC, CONFIG, COMMAND

"""
import sys

module = dir(sys.modules[__name__])
for attr in (a for a in dir(module) if not a.startswith('_')):
	func = getattr(module, attr)
"""

import datetime
from time import time as unixtime
from time import strftime
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
	if type(at) == float:
		at = datetime.datetime.fromtimestamp(at)
		print(at.tzinfo)
	st = at.strftime(_ISO8601_TIME_FORMAT)
	tz = at.tzinfo.tzname(None) if at.tzinfo else 'UTC'
	st += ('Z' if tz == 'UTC' else tz)
	return st

def date(at=None):
	if not at:
		at = now()
	if type(at) == float:
		at = datetime.datetime.fromtimestamp(at)
	st = at.strftime(_DATE_FORMAT)
	return st

def time(at=None):
	if not at:
		at = now()
	if type(at) == float:
		at = datetime.datetime.fromtimestamp(at)
	st = at.strftime(_TIME_FORMAT)
	return st

def utcnow():
	return datetime.datetime.utcnow()

def now():
	return datetime.datetime.now()

def tagometer():
	return (int(strftime("%H")) * 3600 + int(strftime("%M")) * 60 +
		int(strftime("%S"))) / (24 * 36)

def tagometer_view(length=50):
	size = 50 if length > 50 else abs(length)
	percent = tagometer()
	loaded = round(percent / 100 * size)
	toload = size - loaded
	text = "[%s%s] %0.3f%%" % ("#" * loaded, " " * toload, percent)
	return percent if length == 0 else text[::-1] if length < 0 else text

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

class XDict(dict):
	def __init__(self, *args, **kwargs):
		super(XDict, self).__init__(*args, **kwargs)
	def __getattr__(self, name):
		return self.__getitem__(name)

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
			ast.Invert: op.invert,
			ast.Not: op.not_ }

	attrfunctions = {
			str: {
				"capitalize": str.capitalize,
				"format": str.format,
				"index": str.index,
				"isalnum": str.isalnum,
				"isalpha": str.isalpha,
				"isdigit": str.isdigit,
				"islower": str.islower,
				"isspace": str.isspace,
				"istitle": str.istitle,
				"isupper": str.isupper,
				"isprintable": str.isprintable,
				"join": str.join,
				"lower": str.lower,
				"replace": str.replace,
				"split": str.split,
				"splitlines": str.splitlines,
				"startswith": str.startswith,
				"endswith": str.endswith,
				"strip": str.strip,
				"swapcase": str.swapcase,
				"title": str.title,
				"upper": str.upper,
				"zfill": str.zfill },
			dict: {
				"get": dict.get,
				"items": dict.items,
				"keys": dict.keys } }

	constants = {	"pi": math.pi,
			"π": math.pi,
			"e" : math.e,
			"math" : XDict({
				"e": math.e,
				"inf": math.inf,
				"nan": math.nan,
				"pi": math.pi }),
			"True": True,
			"False": False,
			"None": None }

	def search(self, engine, query):
		return self.search_engines[engine] % urlencode(query)

	def _vars(self):
		return self.variables

	def do_eval(self, expression):
		return self.evaluate(expression)

	def do_print(self, *args):
		def allowed(c):
			if c in ["\r", "\n", "\t"]:
				return True
			if ord(c) < 32:
				return False
			return True
		result = " ".join([ str(x) for x in args ])
		result = [ c for c in result if allowed(c) ]
		if len(result) > 750:
			result = result[:750] + ["…"]
		self.send_muc("".join(result))

	def do_lisp(self, code):
		set_print_function(lambda x: self.do_print(x))
		ast = lisp_parse(code)
		return lisp_execute(self.lisp_context, ast)

	functions  = {	"sin": math.sin,
			"cos": math.cos,
			"tan": math.tan,
			"asin": math.asin,
			"acos": math.acos,
			"atan": math.atan,
			"sinh": math.sinh,
			"cosh": math.cosh,
			"tanh": math.tanh,
			"asinh": math.asinh,
			"acosh": math.acosh,
			"atanh": math.atanh,
			"atan2": math.atan2,
			"log": math.log,
			"log2": math.log2,
			"log10": math.log10,
			"exp": math.exp,
			"sqrt": math.sqrt,
			"factorial": math.factorial,
			"trunc": math.trunc,
			"floor": math.floor,
			"ceil": math.ceil,
			"gcd": math.gcd,
			"abs": abs,
			"all": all,
			"any": any,
			"bin": bin,
			"bool": bool,
			"chr": chr,
			"complex": complex,
			"dict": dict,
			"dir": dir,
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
			"set": set,
			"str": str,
			"sum": sum,
			"tuple": tuple,
			"type": type,
			"now": now,
			"utc": utcnow,
			"date": date,
			"time": time,
			"isotime" : isotime,
			"unixtime" : unixtime,
			"uuid": uuid,
			"ping": ping,
			"alive": alive,
			"dnsquery": dnsquery,
			"random": random.random,
			"randrange": random.randrange,
			"oneof": oneof,
			"tagometer": tagometer_view,
			"strftime": strftime
	}

	def __init__(self, search_engine_file=None, **keywords):
		super(Scripting, self).__init__([PRESENCE, MUC, CONFIG,
				COMMAND], name=__name__, **keywords)

		self.search_engine_file = search_engine_file
		self.variables = {}
		self.participants = {}
		self.room_jid = None
		self.lisp_context = create_default_context()

		functions = {
			"search": self.search,
			"vars": self._vars,
			"print": self.do_print,
			"eval": self.do_eval,
			"lisp": self.do_lisp }
		for key in functions.keys():
			self.functions[key] = functions[key]

		self.send_cmd("get_config", key="variables", default={})
		self.send_cmd("get_room_info")
		self.reload_config()

	def reload_config(self):
		self.search_engines = load_database(self.search_engine_file)

	def command(self, cmd, **keywords):
		if cmd == "config_value":
			if keywords["key"] == "variables":
				self.variables = keywords["value"]
		elif cmd == "config_values":
			self.variables = keywords["value"]["variables"]
		elif cmd == "room_info":
			self.participants = {}
			participants = keywords["participants"]
			for participant_jid in participants:
				participant = participants[participant_jid]
				self.participants[participant["nick"]] = \
						participant
			self.room_jid = keywords["jid"]

	def muc_online(self, jid, nick, role, affiliation, **keywords):
		self.participants[nick] = {'jid': jid, 'nick': nick,
				'role': role, 'affiliation': affiliation,
				'time': unixtime()}

	def muc_offline(self, nick, **keywords):
		del self.participants[nick]

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

	def _eval(self, node, var={}):
		if isinstance(node, ast.Num):
			return node.n
		elif isinstance(node, ast.Str):
			return node.s
		elif isinstance(node, ast.Expr):
			return self._eval(node.value, var)
		elif isinstance(node, ast.Return):
			raise ReturnException(self._eval(node.value, var))
		elif isinstance(node, ast.Attribute):
			value = self._eval(node.value, var)
			return value.__getattr__(node.attr)
		elif isinstance(node, ast.List):
			return [ self._eval(x, var) for x in node.elts ]
		elif isinstance(node, ast.Tuple):
			return tuple([ self._eval(x, var) for x in node.elts ])
		elif isinstance(node, ast.Subscript):
			target = self._eval(node.value, var)
			if isinstance(node.slice, ast.Index):
				value = self._eval(node.slice.value, var)
				return target[value]
			else:
				lower = self._eval(node.slice.lower, var)
				upper = self._eval(node.slice.upper, var)
				step = self._eval(node.slice.step, var)
				return target[lower:upper:step]
		elif isinstance(node, ast.ListComp):
			generator = node.generators[0]
			target = [ name.id for name in generator.target.elts ] \
					if type(generator.target) == ast.Tuple \
					else generator.target.id
			items = self._eval(generator.iter, var)
			if len(items) > 100:
				raise Exception('too many iterations')
			var_ = { x : var[x] for x in var }
			def step(x, y, z):
				if type(z) == tuple:
					for i in range(len(y)):
						var_[y[i]] = z[i]
				else:
					var_[y] = z
				result = self._eval(x, var_)
				return result
			if len(generator.ifs) == 0:
				return [ step(node.elt, target, x) \
						for x in items ]
			def ifs(x):
				if type(x) == tuple:
					for i in range(len(target)):
						var_[target[i]] = x[i]
				else:
					var_[target] = x
				v = True
				for i in generator.ifs:
					v = v and self._eval(i, var_)
				return v
			return [ step(node.elt, target, x) for x in items \
					if ifs(x) ]
		elif isinstance(node, ast.Call):
			args = [ self._eval(x, var) for x in node.args ]
			if isinstance(node.func, ast.Attribute):
				obj = node.func.value
				func = node.func.attr
				args = [ self._eval(node.func.value, var) ] \
						+ args
				t = type(args[0])
				if t in self.attrfunctions and \
						func in self.attrfunctions[t]:
					function = self.attrfunctions[t][func]
				else:
					raise NotImplementedError()
			else:
				function = self.functions[node.func.id]
			return function(*args)
		elif isinstance(node, ast.Name):
			if node.id in var:
				return var[node.id]
			elif node.id in self.constants:
				return self.constants[node.id]
			else:
				return self.variables[node.id]
		elif isinstance(node, ast.operator): # <operator>
			return self.operators[type(node)]
		elif isinstance(node, ast.unaryop):
			return self.unaryoperators[type(node)]
		elif isinstance(node, ast.UnaryOp):
			return self._eval(node.op, var)(self._eval(node.operand,
				var))
		elif isinstance(node, ast.BinOp): # <left> <operator> <right>
			operator = self._eval(node.op, var)
			if operator is op.pow:
				right = self._eval(node.right, var)
				if right > 200:
					raise Exception('pow')
			return self._eval(node.op, var)(self._eval(node.left,
					var), self._eval(node.right, var))
		elif isinstance(node, ast.Assign):
			target = node.targets[0].id
			value = self._eval(node.value, var)
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
			left = self._eval(node.left, var)
			value = True
			for i in range(len(node.ops)):
				right = self._eval(node.comparators[i], var)
				value = value and (self.compare(left,
					node.ops[i], right))
				left = right
			return value
		elif isinstance(node, ast.BoolOp):
			if isinstance(node.op, ast.And):
				value = self._eval(node.values[0], var)
				if value == False:
					return False
				for i in range(1, len(node.values)):
					v = self._eval(node.values[i], var)
					value = value and v
					if value == False:
						return False
				return value
			elif isinstance(node.op, ast.Or):
				value = self._eval(node.values[0], var)
				if value == True:
					return True
				for i in range(1, len(node.values)):
					v = self._eval(node.values[i], var)
					value = value or v
					if value == True:
						return True
				return value
			else:
				raise NotImplementedError()
		elif isinstance(node, ast.NameConstant):
			return node.value
		elif isinstance(node, ast.IfExp):
			test = self._eval(node.test, var)
			if test:
				return self._eval(node.body, var)
			else:
				return self._eval(node.orelse, var)
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
		class Participant(dict):
			def __init__(self, *args):
				super(Participant, self).__init__(*args)
			def __getattr__(self, key):
				return self.__getitem__(key)
			def __str__(self):
				return str({'jid': self.jid, 'nick': self.nick,
						'role': self.role,
						'affiliation': self.affiliation,
						'time': self.time})
			def __repr__(self):
				return self.__str__()

		participants = { p : Participant(self.participants[p]) \
				for p in self.participants }
		self.constants['__nick__'] = nick
		self.constants['__jid__'] = jid
		self.constants['__role__'] = role
		self.constants['__affiliation__'] = affiliation
		self.constants['__participants__'] = participants
		self.constants['__room_jid__'] = self.room_jid
		#if re.match(r'^\s*[a-zA-Z0-9]+[\.\s]*$', msg):
		#	return
		if re.match(r'^\s*[0-9]+(\.[0-9]+)?\s*$', msg):
			return
		try:
			#if msg in self.variables:
			#	return
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
				self.do_print(result)
		except SyntaxError:
			pass
		except dns.resolver.NXDOMAIN:
			self.send_muc('Exception: NXDOMAIN')
		except dns.exception.Timeout:
			self.send_muc('Exception: timeout')
		except:
			#traceback.print_exc()
			pass
