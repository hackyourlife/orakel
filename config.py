# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

class Configuration(object):
	def __init__(self, storage, config):
		self.storage = storage
		self.config = config
		self.values = {}
		try:
			self.values = self.storage['config']
		except:
			pass

		for i in ['intrusive']:
			if not i in self.values:
				self.values[i] = False

	def __call__(self, msg, nick, send_message):
		if msg in ['aus!', 'AUS!']:
			self.values['intrusive'] = False
			self.storage['config'] = self.values
			send_message(':(')
			return True
		elif msg in ['an!', 'fass!']:
			self.values['intrusive'] = True
			self.storage['config'] = self.values
			send_message(':)')
			return True
		return False

	def __getattr__(self, name):
		return self.values[name]

	def get(self, section, name):
		return self.config.get(section, name)

	def getint(self, section, name):
		return self.config.getint(section, name)
