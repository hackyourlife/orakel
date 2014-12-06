# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import module
from module import Module
from utils import load_database

class MessageDatabase(Module):
	messages = {}

	def __init__(self, filename, **keywords):
		super(MessageDatabase, self).__init__([module.MUC_MENTION],
				name=__name__, **keywords)
		self.filename = filename
		self.messages = []
		self.reload_config()

	def reload_config(self):
		self.messages = load_database(self.filename)
		self.log.info("%d messages loaded" % len(self.messages))

	def muc_mention(self, msg, **keywords):
		if msg[-1] == '?':
			question = msg[:-1].strip().lower()
		else:
			question = msg.lower()
		if question in self.messages:
			self.send_muc(self.messages[question])
