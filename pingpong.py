# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from module import Module, MUC
from utils import oneof

class PingPong(Module):
	mapping = {
			'ping':		'pong',
			'*ping*':	'*pong*',
			'pink':		'ponk'
			}
	users = {
			'tchab': [
				"Für dich immer noch »pink«!",
				"Klappe zu, Schwulibert!"]
			}


	def __init__(self, **keywords):
		super(PingPong, self).__init__([MUC], **keywords)

	def muc_msg(self, msg, nick, **keywords):
		key = msg.lower()
		if key in self.mapping:
			if nick in self.users:
				self.send_muc(oneof(self.users[nick]))
			else:
				self.send_muc(self.mapping[key])
