# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from utils import strip_jid, oneof
from module import Module, PRESENCE, MUC, COMMAND, CONFIG

class AutoCMD(Module):
	def __init__(self, trollmsg, **keywords):
		super(AutoCMD, self).__init__([PRESENCE, MUC, COMMAND, CONFIG],
				name=__name__, **keywords)
		self.trollmsg = trollmsg
		self.autokick = {'jid': [], 'nick': []}
		self.troll = {'jid': [], 'nick': []}

	def register(self):
		# autokick
		self.send_cmd("register_cli", name=["auto", "kick", "nick"],
				argc=1, undo=True)
		self.send_cmd("register_cli", name=["auto", "kick", "jid"],
				argc=1, undo=True)
		self.send_cmd("register_cli", name=["show", "auto", "kick",
				"nick"], argc=0, undo=False)
		self.send_cmd("register_cli", name=["show", "auto", "kick",
				"jid"], argc=0, undo=False)
		# troll
		self.send_cmd("register_cli", name=["troll", "nick"], argc=1,
				undo=True)
		self.send_cmd("register_cli", name=["troll", "jid"], argc=1,
				undo=True)
		self.send_cmd("register_cli", name=["show", "troll", "nick"],
				argc=0, undo=False)
		self.send_cmd("register_cli", name=["show", "troll", "jid"],
				argc=0, undo=False)

	def unregister(self):
		self.send_cmd("unregister_cli", name=["auto", "kick", "nick"],
				argc=1)
		self.send_cmd("unregister_cli", name=["auto", "kick", "jid"],
				argc=1)
		self.send_cmd("unregister_cli", name=["show", "auto", "kick",
				"nick"], argc=0)
		self.send_cmd("unregister_cli", name=["show", "auto", "kick",
				"jid"], argc=0)
		self.send_cmd("unregister_cli", name=["troll", "nick"], argc=1)
		self.send_cmd("unregister_cli", name=["troll", "jid"], argc=1)
		self.send_cmd("unregister_cli", name=["show", "troll", "nick"],
				argc=0)
		self.send_cmd("unregister_cli", name=["show", "troll", "jid"],
				argc=0)

	def start(self):
		self.send_cmd("get_config", key="autokick",
				default={'jid': [], 'nick': []})
		self.send_cmd("get_config", key="troll",
				default={'jid': [], 'nick': []})
		self.register()

	def stop(self):
		self.unregister()

	def muc_online(self, nick, jid, **keywords):
		jid = strip_jid(jid)
		if nick in self.autokick["nick"]:
			self.kick(nick, "autokick")
		elif jid in self.autokick["jid"]:
			self.kick(nick, "autokick")

	def muc_msg(self, nick, jid, **keywords):
		jid = strip_jid(jid)
		if nick in self.troll["nick"]:
			self.do_troll(nick)
		elif jid in self.troll["jid"]:
			self.do_troll(nick)

	def do_troll(self, nick):
		msg = oneof(self.trollmsg)
		self.send_private(nick, msg, muc=True)

	def command(self, cmd, **keywords):
		if cmd == "reregister_cli":
			self.register()
			return
		elif cmd == "config_value":
			key = keywords["key"]
			value = keywords["value"]
			if key == "autokick":
				self.autokick = value
			elif key == "troll":
				self.troll = value
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
		elif cmd == ["troll", "nick"]:
			self.troll_nick(undo, *args)
		elif cmd == ["troll", "jid"]:
			self.troll_jid(undo, *args)
		elif cmd == ["show", "troll", "nick"]:
			self.show_troll(True)
		elif cmd == ["show", "troll", "jid"]:
			self.show_troll(False)


	def autokick_nick(self, undo, nick):
		if undo:
			if nick in self.autokick["nick"]:
				index = self.autokick["nick"].index(nick)
				del self.autokick["nick"][index]
		elif not nick in self.autokick["nick"]:
			self.autokick["nick"] += [ nick ]
		self.commit()

	def autokick_jid(self, undo, jid):
		jid = strip_jid(jid)
		if undo:
			if jid in self.autokick["jid"]:
				index = self.autokick["jid"].index(jid)
				del self.autokick["jid"][index]
		elif not jid in self.autokick["jid"]:
			self.autokick["jid"] += [ jid ]
		self.commit()

	def troll_nick(self, undo, nick):
		if undo:
			if nick in self.troll["nick"]:
				index = self.troll["nick"].index(nick)
				del self.troll["nick"][index]
		elif not nick in self.troll["nick"]:
			self.troll["nick"] += [ nick ]
		self.commit()

	def troll_jid(self, undo, jid):
		jid = strip_jid(jid)
		if undo:
			if jid in self.troll["jid"]:
				index = self.troll["jid"].index(jid)
				del self.troll["jid"][index]
		elif not jid in self.troll["jid"]:
			self.troll["jid"] += [ jid ]
		self.commit()

	def commit(self):
		self.send_cfg(key="autokick", value=self.autokick)
		self.send_cfg(key="troll", value=self.troll)

	def show_autokick(self, nicks):
		if nicks:
			if len(self.autokick["nick"]) == 0:
				self.send_muc("no autokick nicks configured")
			else:
				self.send_muc("autokick nicks: %s" % \
						", ".join(self.autokick["nick"]))
		else:
			if len(self.autokick["jid"]) == 0:
				self.send_muc("no autokick jids configured")
			else:
				self.send_muc("autokick jids: %s" % \
						", ".join(self.autokick["jid"]))

	def show_troll(self, nicks):
		if nicks:
			if len(self.troll["nick"]) == 0:
				self.send_muc("no troll nicks configured")
			else:
				self.send_muc("troll nicks: %s" % \
						", ".join(self.troll["nick"]))
		else:
			if len(self.troll["jid"]) == 0:
				self.send_muc("no troll jids configured")
			else:
				self.send_muc("troll jids: %s" % \
						", ".join(self.troll["jid"]))
