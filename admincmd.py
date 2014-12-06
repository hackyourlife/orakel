# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from module import Module, COMMAND

class AdminCMD(Module):
	def __init__(self, **keywords):
		super(AdminCMD, self).__init__([COMMAND], **keywords)

	def register(self):
		self.send_cmd("register_cli", name=["kick"], argc=1, undo=False)
		self.send_cmd("register_cli", name=["kick"], argc=2, undo=False)

	def unregister(self):
		self.send_cmd("unregister_cli", name=["kick"], argc=1)
		self.send_cmd("unregister_cli", name=["kick"], argc=2)

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
		if cmd == ["kick"]:
			self.kick(*args)
