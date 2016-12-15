# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet:

from module import Module, MUC
from urllib.parse import quote as urlencode

class Lutcha(Module):
	def __init__(self, **keywords):
		super(Lutcha, self).__init__([MUC], name=__name__, **keywords)

	def muc_msg(self, msg, **keywords):
		parts = msg.strip().split(' ', 1)
		if len(parts) == 2 and parts[0][0] == "!" and \
				parts[0][1:].lower() in ["bash", "doc", "lutcha"]:
			result = self.handle(parts[1], parts[0][1:].lower())
			if result:
				self.send_muc(result)

	def handle(self, msg, cmd):
		parts = msg.strip().split(' ', 1)
		url = "https://luchta.de"
		prefix = "bash " if cmd == "bash" else ""
		if len(parts) == 2 and parts[0][0] == "-":
			return "%s/%s/%s" % (url,
					urlencode(parts[0].lstrip("-")),
					urlencode(prefix + parts[1].strip()))
		elif len(parts) == 1:
			return "%s/%s" % (url, urlencode(prefix +
				" ".join(parts[0])))
		else:
			return
