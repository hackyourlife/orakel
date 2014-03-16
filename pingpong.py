# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

class PingPong(object):
	def __call__(self, msg, nick, send_message):
		result = self.handle(msg.lower())
		if result:
			send_message(result)

	def handle(self, msg):
		if msg == 'ping':
			return 'pong'
		if msg == '*ping*':
			return '*pong*'
		if msg == 'pink':
			return 'ponk'
