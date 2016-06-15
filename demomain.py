#!/bin/python
# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import configparser
import logging
from module import Module
from demomodule import Weather

class Demo(Module):
	def __init__(self):
		super(Demo, self).__init__(name="demo") # unique name
		self.weather = Weather(parent=self) # register sub-modules
		self.log.info("load complete") # send to central logging

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO,
		                        format='%(levelname)-8s %(message)s')

	# create new instance and start it
	demo = Demo()
	try:
		demo.start()
	except KeyboardInterrupt: # kill on ^C
		demo.log.info("unloading")
		demo.stop()
