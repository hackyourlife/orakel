# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from utils import strip_jid
from module import Module, PRESENCE, COMMAND, CONFIG

class AutoCMD(Module):
	def __init__(self, **keywords):
		super(AutoCMD, self).__init__([PRESENCE, COMMAND, CONFIG],
				name=__name__, **keywords)
		self.nicks = []
		self.jids = []

	def register(self):
		self.send_cmd("register_cli", name=["auto", "kick", "nick"],
				argc=1, undo=True)
		self.send_cmd("register_cli", name=["auto", "kick", "jid"],
				argc=1, undo=True)
		self.send_cmd("register_cli", name=["show", "auto", "kick",
				"nick"], argc=0, undo=False)
		self.send_cmd("register_cli", name=["show", "auto", "kick",
				"jid"], argc=0, undo=False)

	def unregister(self):
		self.send_cmd("unregister_cli", name=["auto", "kick", "nick"],
				argc=1)
		self.send_cmd("unregister_cli", name=["auto", "kick", "jid"],
				argc=1)
		self.send_cmd("unregister_cli", name=["show", "auto", "kick",
				"nick"], argc=0)
		self.send_cmd("unregister_cli", name=["show", "auto", "kick",
				"jid"], argc=0)

	def start(self):
		self.send_cmd("get_config", key="autokick", default=None)
		self.register()

	def stop(self):
		self.unregister()

	def muc_online(self, nick, jid, **keywords):
		jid = strip_jid(jid)
		if nick in self.nicks:
			self.kick(nick, "autokick")
		elif jid in self.jids:
			self.kick(nick, "autokick")

	def command(self, cmd, **keywords):
		if cmd == "reregister_cli":
			self.register()
			return
		elif cmd == "config_value":
			key = keywords["key"]
			if key == "autokick":
				value = keywords["value"]
				if value is None:
					value = {'jid': [], 'nick': []}
				self.nicks = value["nick"]
				self.jids = value["jid"]
			return
		if cmd != "cli_cmd":
			return
		cmd = keywords["command"]
		args = keywords["args"]
		undo = keywords["undo"]
		if cmd == ["auto", "kick", "nick"]:
			self.autokick_nick(undo, *args)
		elif cmd == ["auto", "kick", "jid"]:
			self.autokick_jid(undo, *args)
		elif cmd == ["show", "auto", "kick", "nick"]:
			self.show_autokick(True)
		elif cmd == ["show", "auto", "kick", "jid"]:
			self.show_autokick(False)

	def autokick_nick(self, undo, nick):
		if undo:
			if nick in self.nicks:
				index = self.nicks.index(nick)
				del self.nicks[index]
		elif not nick in self.nicks:
			self.nicks += [ nick ]
		self.commit()

	def autokick_jid(self, undo, jid):
		jid = strip_jid(jid)
		if undo:
			if jid in self.jids:
				index = self.jids.index(jid)
				del self.jids[index]
		elif not jid in self.jids:
			self.jids += [ jid ]
		self.commit()

	def commit(self):
		value = {'jid': self.jids, 'nick': self.nicks}
		self.send_cfg(key="autokick", value=value)

	def show_autokick(self, nicks):
		if nicks:
			self.send_muc("autokick nicks: %s" % \
					", ".join(self.nicks))
		else:
			self.send_muc("autokick jids: %s" % \
					", ".join(self.jids))
