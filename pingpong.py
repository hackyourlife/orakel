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
		key = msg.lower()
		if key in self.mapping:
			if nick in self.users and key in self.users[nick]:
				self.send_muc(oneof(self.users[nick][key]))
			else:
				self.send_muc(self.mapping[key])

	def muc_mention(self, msg, nick, **keywords):
		key = msg.lower()
		if key in self.mapping:
			if nick in self.users and key in self.users[nick]:
				self.send_muc("%s: %s" % \
						(nick,
						oneof(self.users[nick][key])))
			else:
				self.send_muc("%s: %s" % \
						(nick, self.mapping[key]))
