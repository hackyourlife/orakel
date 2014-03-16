# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

class Count(object):
	def __call__(self, msg, nick, send_message):
		try:
			i = int(msg) + 1
			if i == 42:
				send_message("42!")
			elif i == 21:
				send_message("42 / 2")
			else:
				send_message(str(i))
			return True
		except:
			return False
