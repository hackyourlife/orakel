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
		index = self.muted.find(nick)
		del self.muted[index]
		self.storage['muted'] = self.muted

	def talk_muted(self, msg, nick, send_message):
		if nick in self.muted:
			return True
		return False
