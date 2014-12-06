# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import os
import json
from module import Module, CONFIG, COMMAND

class Storage(Module):
	def __init__(self, filename, **keywords):
		super(Storage, self).__init__([CONFIG, COMMAND], **keywords)
		self.values = {}
		self.filename = filename
		if os.path.isfile(filename):
			self.load()
			self.save()

	def load(self):
		with open(self.filename, "r") as f:
			self.values = json.loads(f.read())

	def save(self):
		with open(self.filename, "w") as f:
			f.write(json.dumps(self.values))

	def command(self, cmd, **keywords):
		if cmd == 'get_config':
			if 'key' in keywords:
				key = keywords['key']
				self.send_cmd('config_value', key=key,
						value=self.__getitem__(key))
			else:
				self.publish_all()

	def config_change(self, key, value):
		self.log.info("config change: '%s'='%s'" % (key, value))
		self.__setitem__(key, value)

	def reload_config(self):
		self.load()
		self.publish_all()

	def publish_all(self):
		self.send_cmd('config_values', value=self.values)

	def __getitem__(self, key):
		return self.values[key]

	def __setitem__(self, key, value):
		self.values[key] = value
		self.save()

	def __getattr__(self, key):
		return self.values[key]

	def __setattr_(self, key, value):
		self.values[key] = value
		self.save()
