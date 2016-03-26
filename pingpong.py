# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from module import Module, MUC, MUC_MENTION
from utils import oneof

class PingPong(Module):
	mapping = {
			'ping':		'pong',
			'*ping*':	'*pong*',
			'pink':		'ponk'
			}
	users = {
			'tchab': {
				'ping':  [ "Für dich immer noch »pink«!",
					"Klappe zu, Schwulibert!"],
				'*ping*': [ "Für dich immer noch »pink«!",
					"Klappe zu, Schwulibert!" ]
			}
		}


	def __init__(self, **keywords):
		super(PingPong, self).__init__([MUC, MUC_MENTION], **keywords)

	def muc_msg(self, msg, nick, **keywords):
		self.pingpong(msg, nick, "%s")

	def muc_mention(self, msg, nick, **keywords):
		self.pingpong(msg, nick, "%s: %%s" % nick)

	def pingpong(self, msg, nick, formatstr):
		key = msg.lower()
		if key in self.mapping:
			if nick in self.users and key in self.users[nick]:
				self.send_muc(formatstr % \
						oneof(self.users[nick][key]))
			else:
				self.send_muc(formatstr % \
						self.mapping[key])

