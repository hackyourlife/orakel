# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from module import Module, PRESENCE, CONFIG, COMMAND

class Mute(Module):
	def __init__(self, **keywords):
		super(Mute, self).__init__([PRESENCE, CONFIG, COMMAND],
				name=__name__, **keywords)

	def register(self):
		self.send_cmd("register_cli", name=["mute"], argc=1, undo=True)
		self.send_cmd("register_cli", name=["show", "mute"], argc=0,
				undo=False)

	def unregister(self):
		self.send_cmd("unregister_cli", name=["mute"], argc=1)
		self.send_cmd("unregister_cli", name=["show", "mute"], argc=0)

	def start(self):
		self.send_cmd("get_config", key="muted", default=[])
		self.register()

	def stop(self):
		self.unregister()

	def command(self, cmd, **keywords):
		if cmd == "reregister_cli":
			self.register()
			return
		elif cmd == "config_value":
			key = keywords["key"]
			if key == "muted":
				self.muted = keywords["value"]
		elif cmd == "cli_cmd":
			undo = keywords["undo"]
			args = keywords["args"]
			command = keywords["command"]
			caller_nick = keywords["caller_nick"]
			if command == ["show", "mute"]:
				self.show_mute(*args)
			elif command == ["mute"]:
				self.mute_command(caller_nick, undo, *args)

	def mute(self, nick):
		if not nick in self.muted:
			self.muted += [ nick ]
		self.send_cfg(key="muted", value=self.muted)
		self.set_role(nick, 'visitor')

	def unmute(self, nick):
		if not nick in self.muted:
			return
		index = self.muted.index(nick)
		del self.muted[index]
		self.send_cfg(key="muted", value=self.muted)
		self.set_role(nick, 'participant')

	def is_muted(self, nick):
		return nick in self.muted

	def muc_online(self, nick, **keywords):
		if nick in self.muted:
			self.set_role(nick, 'visitor')

	def show_mute(self):
		self.send_muc("currently muted: %s" % ", ".join(self.muted))

	def mute_command(self, caller_nick, undo, nick):
		if nick == caller_nick:
			return
		if undo:
			if self.is_muted(nick):
				self.unmute(nick)
				self.send_muc('unmuted "%s"' % nick)
			else:
				self.send_muc('"%s" is not muted' % nick)
		else:
			if self.is_muted(nick):
				self.send_muc('"%s" is already muted' % nick)
			else:
				self.mute(nick)
				self.send_muc('muted "%s"' % nick)
