# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from module import Module, MUC

class Masochist(Module):
	def __init__(self, **keywords):
		super(Masochist, self).__init__([MUC], name=__name__,
				**keywords)

	def muc_msg(self, nick, msg, **keywords):
		tokens = msg.strip().split(" ")
		if tokens == ["kick", nick]:
			self.kick(nick)
