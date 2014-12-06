# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from module import Module, MUC, COMMAND
from utils import startswith, parse

class CLI(Module):
	def __init__(self, **keywords):
		super(CLI, self).__init__([MUC, COMMAND], name=__name__,
				**keywords)
		self.handlers = {}
		self.send_cmd("reregister_cli")
		self.send_cmd("init_value", key="intrusive", value=False)

	def muc_msg(self, msg, nick, jid, role, **keywords):
		if msg in ["aus!", "AUS!"]:
			self.send_cfg("intrusive", False)
			self.send_muc(":(")
		elif msg in ["an!", "fass!"]:
			self.send_cfg("intrusive", True)
			self.send_muc(":)")
		elif role == "moderator":
			self.statement(nick, jid, msg)

	def command(self, cmd, **args):
		if cmd == "register_cli":
			command = args["name"]
			argc = args["argc"]
			undo = True
			if "undo" in args:
				undo = args["undo"]
			info = []
			if type(command) == list:
				info = command[1:]
				command = command[0]
			if not command in self.handlers:
				self.handlers[command] = []
			handler = [{'argc': argc, 'info': info, 'undo' : undo}]
			if not handler in self.handlers[command]:
				self.handlers[command] += handler
				c = [command]
				if len(info) > 0:
					c += info
				c = " ".join(c)
				self.log.info("command registered: \"%s\" " \
						"(%d args)" % (c, argc))
		elif cmd == "unregister_cli":
			command = args["name"]
			argc = args["argc"]
			info = []
			if type(command) == list:
				info = command[1:]
				command = command[0]
			if command in self.handlers:
				for i in range(len(self.handlers[command])):
					handler = self.handlers[command][i]
					if handler["info"] == info and \
							handler["argc"] == argc:
						del self.handlers[command][i]
						c = [command]
						if len(info) > 0:
							c += info
						c = " ".join(c)
						self.log.info("command " \
								"removed: " \
								"\"%s\" " \
								"(%d args)" %
								(c, argc))
						break

	def statement(self, caller_nick, caller_jid, msg):
		try:
			parts = parse(msg)
		except SyntaxError:
			return
		if len(parts) == 0:
			return False
		command = parts[0]
		undo = False
		data = parts[1:]
		cmdline = msg.strip()
		if command == 'no':
			undo = True
			command = parts[1]
			data = parts[2:]
		if not command in self.handlers:
			return
		if undo and command == 'show': # "no show" is invalid
			return

		for handler in self.handlers[command]:
			if startswith(data, handler['info']):
				canundo = handler['undo']
				if undo and not canundo:
					continue
				args = data[len(handler['info']):]
				if type(handler['argc']) == list:
					if not len(args) in handler['argc']:
						continue
				elif len(args) != handler['argc']:
					continue
				cmd = [command]
				if len(handler['info']) > 0:
					cmd += handler['info']
				self.send_cmd('cli_cmd', args=args,
						cmdline=cmdline, undo=undo,
						command=cmd,
						caller_nick=caller_nick,
						caller_jid=caller_jid)
