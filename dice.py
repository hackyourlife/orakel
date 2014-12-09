# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import re
from utils import randrange
from module import Module, MUC

class Dice(Module):
	def __init__(self, **keywords):
		super(Dice, self).__init__([MUC], name=__name__, **keywords)

	def muc_msg(self, msg, nick, **keywords):
		r = r'^([0-9]+)d([0-9]+)$'
		match = re.match(r, msg)
		if match:
			dice = int(match.group(1))
			eyes = int(match.group(2))
			result = sum([ randrange(1, eyes + 1) \
					for x in range(dice)])
			self.send_muc(str(result))
