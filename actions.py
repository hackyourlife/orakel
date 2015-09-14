# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from utils import oneof
from re import match
import datetime
import uuid as guid
import icmplib

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
		at = utcnow()
	st = at.strftime(_DATE_FORMAT)
	return st

def time(at=None):
	if not at:
		at = utcnow()
	st = at.strftime(_TIME_FORMAT)
	return st

def utcnow():
	"""Overridable version of utils.utcnow."""
	return datetime.datetime.utcnow()


class Actions(object):
	"""
		if(/^bist du ein bot\??$/i.test(msg))
			return 'Nein';
		if(/^(wer|was) bist du\??$/i.test(msg))
			return 'das Orakel';
		if(/^was machst du\??$/i.test(msg))
			return 'existieren';
		if(/^wer ist dein meister\??$/i.test(msg))
			return '/me hat keinen Meister';
		if(/^ist das schlimm\??$/i.test(msg))
			return oneof(['ja', 'nein', 'vielleicht']);
		if(/^stimmt das\??$/i.test(msg) || /^stimmt das[, ]/i.test(msg))
			return oneof(['ja', 'nein']);
		if(/^ist das falsch\??/i.test(msg))
			return oneof(['nein', 'ja']);
		if(/^(wie spät(ist es)?|zeit)\??/i.test(msg))
			return new Date();
	"""

	def __init__(self, storage):
		self.storage = storage
		self.actions = {
			"sag": self.sag,
			"merke": self.merke,
			"sprich": self.sprich,
			"ping": self.ping }
		self.directactions = {
			"stimmt das": self.stimmt_das,
			"ist das schlimm": self.ist_das_schlimm,
			"ist das falsch": self.ist_das_falsch,
			"zeit": self.time,
			"utc": isotime,
			"guid": uuid,
			"uuid": uuid,
			"isotime": isotime,
			"datum": self.date }
		self.regex = {
			"^bist du ein bot\\??$": "Nein",
			"^(wer|was) bist du\\??$": "das Orakel" }
		self.passive_actions = {
			"!ping": self.ping }
		self.passive_directactions = {
			"!utc": isotime,
			"!now": self.now,
			"!uuid": uuid,
			"!date": self.date,
			"!time": self.time }

	def sag(self, args):
		return args

	def merke(self, args):
		self.storage["remembered"] = args
		return False

	def sprich(self, args):
		return self.storage["remembered"]

	def stimmt_das(self):
		return oneof(["ja", "nein"])

	def ist_das_schlimm(self):
		return oneof(["ja", "nein", "vielleicht"])

	def ist_das_falsch(self):
		return oneof(["ja", "nein"])

	def now(self):
		return isotime(datetime.datetime.now())

	def date(self):
		return date(datetime.datetime.now())

	def time(self):
		return time(datetime.datetime.now())

	def ping(self, addr):
		if len(addr.strip()) == 0:
			return "pong"
		addr = addr.split(" ")[0].strip()
		try:
			result = icmplib.ping(addr)
			if not result:
				return "Request timed out"
			else:
				return "%1.2fms" % (result * 1000)
		except:
			return None

	def active(self, msg, nick, send_message):
		direct = msg[:-1].strip() if msg[-1] == '?' else msg
		if direct in self.directactions:
			action = self.directactions[direct]
			result = action if type(action) == str else action()
			send_message(result)
			return True
		tokens = msg.split(" ")
		action = tokens[0].strip()
		args = " ".join(tokens[1:]).strip()
		if action in self.actions:
			result = self.actions[action](args)
			if result:
				send_message(result)
				return True
		return False

	def passive(self, msg, nick, send_message):
		direct = msg[:-1].strip() if msg[-1] == '?' else msg
		if direct in self.passive_directactions:
			action = self.passive_directactions[direct]
			result = action if type(action) == str else action()
			send_message(result)
			return True
		tokens = msg.split(" ")
		action = tokens[0].strip()
		args = " ".join(tokens[1:]).strip()
		if action in self.passive_actions:
			result = self.passive_actions[action](args)
			if result:
				send_message(result)
				return True
		return False
