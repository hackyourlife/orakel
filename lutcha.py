# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet:

from module import Module, MUC
from urllib.parse import quote as urlencode

class Lutcha(Module):
	def __init__(self, **keywords):
		super(Lutcha, self).__init__([MUC], name=__name__, **keywords)

	def muc_msg(self, msg, **keywords):
		parts = msg.split(' ', 1)
		if len(parts) == 2 and parts[0][0] == "!" and parts[0][1:].lower() in ["bash", "doc", "lutcha"]:
			result = self.handle(msg)
			if result:
				self.send_muc(result)

	def handle(self, msg):
		parts = msg.split(' ', 2)
		cmd = parts[0].lower()
		url = "https://luchta.de"
		if cmd == "bash":
			url += "/bash"
		if len(parts) == 3 and parts[1][0] == "-":
			return "%s/%s/%s" % (url,
					urlencode(parts[1].lstrip("-")),
					urlencode(parts[2]))
		elif len(parts) > 1:
			return "%s/%s" % (url, urlencode(" ".join(parts[1:])))
		else:
			return
