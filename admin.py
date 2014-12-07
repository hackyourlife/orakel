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
	def __init__(self, trollmsg):
		super(Admin, self).__init__(name="admin")
		self.admincmd = AdminCMD(parent=self)
		self.autocmd = AutoCMD(trollmsg, parent=self)
		self.mute = Mute(parent=self)
		self.log.info("load complete")

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO,
		                        format='%(levelname)-8s %(message)s')

	filename = "orakel.cfg"
	config = configparser.SafeConfigParser()
	config.read(filename)
	troll = config.get("modules", "troll")
	troll = [x.strip() for x in troll.split(';') if x.strip() != '']
	admin = Admin(troll)
	try:
		admin.start()
	except KeyboardInterrupt:
		admin.log.info("unloading")
		admin.stop()
