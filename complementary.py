#!/bin/python
# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import configparser
import logging
from module import Module
from scripting import Scripting
from cookies import Cookies
from dice import Dice
from masochist import Masochist
from online import Online

class Complementary(Module):
	def __init__(self, search_engines):
		super(Complementary, self).__init__(name="complementary")
		self.scripting = Scripting(search_engines, parent=self)
		self.cookies = Cookies(parent=self)
		self.dice = Dice(parent=self)
		self.masochist = Masochist(parent=self)
		self.online = Online(parent=self)
		self.log.info("load complete")

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO,
		                        format='%(levelname)-8s %(message)s')

	filename = "orakel.cfg"
	config = configparser.SafeConfigParser()
	config.read(filename)
	search_engines = config.get("db", "searchengines")
	complementary = Complementary(search_engines)
	try:
		complementary.start()
	except KeyboardInterrupt:
		complementary.log.info("unloading")
		complementary.stop()
