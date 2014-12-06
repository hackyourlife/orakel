#!/bin/python
# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import configparser
import logging
from module import Module
from storage import Storage
from msgdatabase import MessageDatabase
from search import Search
from pingpong import PingPong

class Core(Module):
	def __init__(self, questions, search_engines, storage):
		super(Core, self).__init__(name="core")
		self.storage = Storage(storage, parent=self)
		self.messages = MessageDatabase(questions, parent=self)
		self.search = Search(search_engines, parent=self)
		self.pingpong = PingPong(parent=self)
		self.log.info("load complete")

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO,
		                        format='%(levelname)-8s %(message)s')

	filename = "orakel.cfg"
	config = configparser.SafeConfigParser()
	config.read(filename)
	questions = config.get("db", "questions")
	search_engines = config.get("db", "searchengines")
	storage = config.get("db", "storage")
	core = Core(questions, search_engines, storage)
	try:
		core.start()
	except KeyboardInterrupt:
		core.log.info("unloading")
		core.stop()
