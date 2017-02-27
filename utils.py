# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from random import SystemRandom

def randrange(*args):
	return SystemRandom().randrange(*args)

def oneof(values, *args):
	if len(args) == 0:
		return SystemRandom().choice(values)
	else:
		return SystemRandom().choice([values] + list(args))

def startswith(a, b):
	if len(b) > len(a):
		return False
	if len(b) == 0:
		return True
	for i in range(len(b)):
		if a[i] != b[i]:
			return False
	return True

def load_database(filename):
	database = {}
	with open(filename, "r") as f:
		for line in f.readlines():
			line = line.strip()
			parts = line.split(";")
			key = parts[0].strip().lower()
			value = ";".join(parts[1:]).strip()
			database[key] = value
	return database

def parse(line):
	tokens = []
	token = []
	instring = False

	for i in range(len(line)):
		c = line[i]
		if instring:
			if c == '"':
				instring = False
			else:
				token += [c]
		elif c == '"':
			instring = True
		elif c in ['\t', '\r', '\n', ' ']:
			if len(token) != 0:
				tokens += [ "".join(token) ]
				token = []
		else:
			token += [c]
	if instring:
		raise SyntaxError("missing dquote")
	if len(token) != 0:
		tokens += [ "".join(token) ]

	return tokens

def split_jid(jid):
	try:
		p1 = jid.index('@')
	except ValueError:
		raise SyntaxError('not a valid jid')
	p2 = None
	try:
		p2 = jid.index('/', p1)
	except ValueError: pass
	user = jid[0:p1]
	host = jid[p1 + 1:p2]
	resource = None if not p2 else jid[p2 + 1:]
	return [user, host, resource]

def strip_jid(jid):
	tokens = split_jid(jid)
	return "%s@%s" % (tokens[0], tokens[1])
