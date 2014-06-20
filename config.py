# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from utils import startswith

class Configuration(object):
	def __init__(self, storage, config):
		self.storage = storage
		self.config = config
		self.values = {}
		self.handlers = {}
		try:
			self.values = self.storage['config']
		except:
			pass

		for i in ['intrusive']:
			if not i in self.values:
				self.values[i] = False

	def add_handler(self, command, handler=None):
		info = []
		if type(command) == list:
			info = command[1:]
			command = command[0]
		if not command in self.handlers:
			self.handlers[command] = []
		self.handlers[command] += [{'handler': handler, 'info': info}]

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
		else:
			return self.passive_config(msg, nick, send_message)
		return False

	def passive_config(self, msg, nick, send_message):
		parts = [ x.strip() for x in msg.strip().split(' ') if
				x.strip() != '' ]
		if len(parts) == 0:
			return False
		command = parts[0]
		undo = False
		data = parts[1:]
		args = {'send_message': send_message, 'cmdline': msg.strip() }
		if command == 'no':
			undo = True
			command = parts[1]
			data = parts[2:]
		if not command in self.handlers:
			return False
		if undo and command == 'show': # "no show" is invalid
			return False
		if command != 'show':
			data = [ undo ] + data
		for handler in self.handlers[command]:
			if startswith(data, handler['info']):
				data = data[len(handler['info']):]
				if handler['handler'] is None:
					continue
				try:
					handler['handler'](*data, **args)
					return True
				except:
					pass

	def __getattr__(self, name):
		return self.values[name]

	def get(self, section, name):
		return self.config.get(section, name)

	def getint(self, section, name):
		return self.config.getint(section, name)
