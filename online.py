# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from module import Module, MUC_MENTION

class Online(Module):
	def __init__(self, **keywords):
		super(Online, self).__init__([MUC_MENTION], name=__name__,
				**keywords)
		self.send_cmd("get_room_info")

	def muc_mention(self, msg, **keywords):
		if not (msg.startswith("ist ") and (msg.endswith(" online?") \
				or msg.endswith(" online"))):
			return
		u = msg[4:-8].strip()
		if len(u) == 0:
			return
		for n in self.participants:
			if u == n or u + "@webchat" == n \
					or self.participants[n]["jid"].split("@")[0] == u:
				self.send_muc("Ja, %s ist online." % n)
				return
		self.send_muc("Nein, %s ist nicht online." % u)
