# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from urllib.parse import quote as urlencode
import module
from module import Module
from utils import load_database

class Search(Module):
	def __init__(self, filename, **keywords):
		super(Search, self).__init__([module.MUC], name=__name__,
				**keywords)
		self.filename = filename
		self.reload_config()

	def reload_config(self):
		self.search_engines = load_database(self.filename)
		self.log.info("%d search engines loaded" %
				len(self.search_engines))

	def muc_msg(self, msg, **keywords):
		if msg[0] != "!":
			return
		tokens = msg[1:].split(" ")
		engine = tokens[0].strip()
		if len(engine) < 1:
			return
		if engine[-1] == ":":
			engine = engine[:-1]
		if len(engine) < 1:
			return
		question = " ".join(tokens[1:]).strip()
		if engine in self.search_engines:
			self.send_muc(self.search_engines[engine] %
					urlencode(question))
