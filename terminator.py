# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from module import Module, COMMAND

class Terminator(Module):
	def __init__(self, **keywords):
		super(Terminator, self).__init__([COMMAND], name=__name__,
				**keywords)
		self.target = None

	def register(self):
		self.send_cmd("register_cli", name=["set", "target"], argc=1,
				undo=False)
		self.send_cmd("register_cli", name=["kill", "it"], argc=0,
				undo=False)

	def unregister(self):
		self.send_cmd("unregister_cli", name=["set", "target"], argc=1)
		self.send_cmd("unregister_cli", name=["kill", "it"], argc=0)

	def start(self):
		self.register()

	def stop(self):
		self.unregister()

	def command(self, cmd, **keywords):
		if cmd == "reregister_cli":
			self.register()
			return
		if cmd != "cli_cmd":
			return
		cmd = keywords["command"]
		args = keywords["args"]
		if cmd == ["set", "target"]:
			self.target = args[0]
			self.send_muc("ok, my lord")
		elif cmd == ["kill", "it"]:
			if not self.target is None:
				self.kick(self.target, "Headshot!")
				self.target = None
			else:
				self.send_muc("no target.")
