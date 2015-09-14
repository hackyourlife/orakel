# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

class Operators(object):
	def __init__(self, storage, config):
		self.storage = storage
		try:
			self.ops = storage['op']
		except:
			self.ops = [ op.strip() for op in config.split(",") ]
		for nick in config.split(","):
			if not self.is_op(nick.strip()):
				self.ops += [ nick.strip() ]

	def op(self, nick):
		if not nick in self.ops:
			self.ops += [ nick ]
		self.storage['op'] = self.ops

	def deop(self, nick):
		if not nick in self.ops:
			return
		index = self.ops.index(nick)
		del self.ops[index]
		self.storage['op'] = self.ops

	def is_op(self, nick):
		return nick in self.ops

	def show_handler(self, *args, **keywords):
		send_message = keywords['send_message']
		if len(args) == 0:
			send_message('ops: %s' % ", ".join(self.ops))

	def config_handler(self, undo, *args, **keywords):
		send_message = keywords['send_message']
		if len(args) == 0:
			print("args: %s" % args)
			return
		nick = " ".join(args)
		if nick == keywords['nick']:
			return
		if undo:
			if self.is_op(nick):
				self.deop(nick)
				send_message('deoped "%s"' % nick)
			else:
				send_message('"%s" is not an op' % nick)
		else:
			if self.is_op(nick):
				send_message('"%s" is already an op' % nick)
			else:
				self.op(nick)
				send_message('oped "%s"' % nick)
