#!/bin/python
# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import configparser
import logging
from module import Module
from admincmd import AdminCMD
from autocmd import AutoCMD
from mute import Mute

class Admin(Module):
	def __init__(self):
		super(Admin, self).__init__(name="admin")
		self.admincmd = AdminCMD(parent=self)
		self.autocmd = AutoCMD(parent=self)
		self.mute = Mute(parent=self)
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
	maxlength = config.getint("modules", "flooding")
	paste = config.get("modules", "paste")
	admin = Admin()
	try:
		admin.start()
	except KeyboardInterrupt:
		admin.log.info("unloading")
		admin.stop()
