# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

class Mute(object):
	def __init__(self, storage):
		self.storage = storage
		self.muted = storage['muted']

	def mute(self, nick):
		if not nick in self.muted:
			self.muted += [ nick ]
		self.storage['muted'] = self.muted

	def unmute(self, nick):
		if not nick in self.muted:
			return
		index = self.muted.index(nick)
		del self.muted[index]
		self.storage['muted'] = self.muted

	def is_muted(self, nick):
		return nick in self.muted

	def talk_muted(self, msg, nick, send_message):
		if nick in self.muted:
			return True
		return False

	def show_handler(self, *args, **keywords):
		send_message = keywords['send_message']
		if len(args) == 0:
			send_message('currently muted: %s' % \
					", ".join(self.muted))

	def config_handler(self, undo, *args, **keywords):
		send_message = keywords['send_message']
		if len(args) != 1:
			print("args: %s" % args)
			return
		nick = args[0]
		if undo:
			if self.is_muted(nick):
				self.unmute(nick)
				send_message('unmuted "%s"' % nick)
			else:
				send_message('"%s" is not muted' % nick)
		else:
			if self.is_muted(nick):
				send_message('"%s" is already muted' % nick)
			else:
				self.mute(nick)
				send_message('muted "%s"' % nick)
