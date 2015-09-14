#!/bin/python
# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import sys
import configparser
import logging
from client import Client
from learning import Learning

if sys.version_info < (3, 0):
	reload(sys)
	sys.setdefaultencoding('utf8')

def load_database(filename):
	database = {}
	with open(filename, "r") as f:
		for line in f.readlines():
			line = line.strip()
			parts = line.split(";")
			key = parts[0].strip().lower()
			value = ";".join(parts[1:]).strip()
			database[key] = value
	return database

if __name__ == "__main__":
	filename = "supporter.cfg"
	config = configparser.SafeConfigParser()
	config.read(filename)

	jid = config.get("xmpp", "jid")
	password = config.get("xmpp", "password")
	room = config.get("xmpp", "room")
	nick = config.get("xmpp", "nick")

	logging.basicConfig(level=logging.INFO,
		                        format='%(levelname)-8s %(message)s')

	words = config.get("brain", "words")
	synonyms = config.get("brain", "synonyms")
	thoughts = config.get("brain", "thoughts")
	messages = config.get("brain", "messages")
	state = config.get("brain", "state")
	brain = Learning(words, synonyms, thoughts, messages, state)

	xmpp = Client(jid, password, room, nick)
	xmpp.register_plugin('xep_0030') # Service Discovery
	xmpp.register_plugin('xep_0045') # Multi-User Chat
	xmpp.register_plugin('xep_0199') # XMPP Ping
	def do_brain(nick, msg, **keywords):
		brain(msg, nick, xmpp.muc_send)
	xmpp.add_message_listener(do_brain)
	if xmpp.connect():
		xmpp.process(block=True)
	else:
		print("Unable to connect")
