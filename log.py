# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

class Log(object):
	def __init__(self, name, send):
		self.name = name
		self.send = send

	def log(self, severity, msg):
		self.send(msg, severity, self.name)

	def debug(self, msg):
		self.log('DEBUG', msg)

	def info(self, msg):
		self.log('INFO', msg)

	def warn(self, msg):
		self.log('WARN', msg)

	def error(self, msg):
		self.log('ERROR', msg)

	def critical(self, msg):
		self.log('CRITICAL', msg)

	def fatal(self, msg):
		self.log('FATAL', msg)
