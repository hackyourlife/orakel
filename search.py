# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from urllib.parse import quote as urlencode

class Search(object):
	def __init__(self, search_engines):
		self.search_engines = search_engines

	def __call__(self, msg, nick, send_message):
		if msg[0] != "!":
			return False
		tokens = msg[1:].split(" ")
		engine = tokens[0].strip()
		if engine[-1] == ":":
			engine = engine[:-1]
		question = " ".join(tokens[1:]).strip()
		if engine in self.search_engines:
			send_message(self.search_engines[engine] %
					urlencode(question))
			return True
		return False
