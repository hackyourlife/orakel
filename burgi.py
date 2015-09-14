# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

class Burgi(object):
	def __call__(self, msg, nick, send_message):
		result = self.handle(msg.lower(),nick)
		if result:
			send_message(result)
			return True
		return False

	def handle(self, msg, nick):
		if nick == 'burgi' or 'local _@_/°':
			if '*' in msg:
				if 'duck' in msg or 'duckt' in msg:
					return '/me holt Burgi zurück und verstreut Schnecken-Gift'
