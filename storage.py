# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import os
import json

class Storage(object):
	def __init__(self, filename):
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
