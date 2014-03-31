# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from time import time

class Alphabet(object):
	def __init__(self, storage, config):
		self.storage = storage
		self.config = config
		try:
			self.storage['lastalphabet']
		except:
			self.storage['lastalphabet'] = 0
		self.noalphabet = config.get("modules", "noalphabet").split(",")

	def action(self, msg, nick, send_message):
		if len(msg) != 1:
			return False
		ch = msg[0]
		if ch in self.noalphabet:
			return False
		if ch >= 'a' and ch <= 'z':
			ch = chr(ord('a') + ((ord(ch) - ord('a')) + 1) % 26)
			send_message(ch)
			return True
		if ch >= 'A' and ch <= 'Z':
			ch = chr(ord('A') + ((ord(ch) - ord('A')) + 1) % 26)
			send_message(ch)
			return True

	def __call__(self, msg, nick, send_message):
		if not self.config.intrusive:
			return False
		t = time()
		if (t - self.storage['lastalphabet']) < \
				self.config.getint("timeouts", "alphabet"):
			return False
		if not self.action(msg, nick, send_message):
			return False
		self.storage['lastalphabet'] = t
		return True
