# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from time import time

class Count(object):
	def __init__(self, storage, config):
		self.storage = storage
		self.config = config
		try:
			self.storage['lastcount']
		except:
			self.storage['lastcount'] = 0

	def action(self, msg, nick, send_message):
		try:
			i = int(msg) + 1
			if i == 42:
				send_message("42!")
			elif i == 21:
				send_message("42 / 2")
			else:
				send_message(str(i))
			return True
		except:
			return False

	def __call__(self, msg, nick, send_message):
		if not self.config.intrusive:
			return False
		t = time()
		if (t - self.storage['lastcount']) < \
				self.config.getint("timeouts", "count"):
			return False
		if not self.action(msg, nick, send_message):
			return False
		self.storage['lastcount'] = t
		return True
