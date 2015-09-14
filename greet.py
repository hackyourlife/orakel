# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from utils import oneof

class Greet(object):
	def __init__(self, greetings, nick):
		self.greetings = greetings
		self.nick = nick
		self.g = [ "%s %s" % (g, self.nick) for g in self.greetings ]

	def __call__(self, msg, nick, send_message):
		if msg in self.g:
			send_message(oneof(self.greetings))
			return True
		return False
