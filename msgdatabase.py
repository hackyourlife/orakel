# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import logging

class MessageDatabase(object):
	messages = {}

	def __init__(self, questions):
		self.messages = questions
		self.logger = logging.getLogger("orakel.msgdatabase")
		self.logger.info("%d messages loaded" % len(self.messages))

	def __call__(self, msg, nick, send_message):
		if msg[-1] == '?':
			question = msg[:-1].strip().lower()
		else:
			question = msg.lower()
		if question in self.messages:
			send_message(self.messages[question])
			return True
		return False
