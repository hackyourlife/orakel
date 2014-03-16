# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

class Alphabet(object):
	def __call__(self, msg, nick, send_message):
		if len(msg) != 1:
			return False
		ch = msg[0]
		if ch >= 'a' and ch <= 'z':
			ch = chr(ord('a') + ((ord(ch) - ord('a')) + 1) % 26)
			send_message(ch)
			return True
		if ch >= 'A' and ch <= 'Z':
			ch = chr(ord('A') + ((ord(ch) - ord('A')) + 1) % 26)
			send_message(ch)
			return True
