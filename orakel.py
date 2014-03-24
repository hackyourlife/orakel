#!/bin/python
# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import sys
import configparser
import logging
from client import Client
from msgdatabase import MessageDatabase
from pingpong import PingPong
from alphabet import Alphabet
from count import Count
from search import Search
from greet import Greet
#from expression import Expression
from actions import Actions
from storage import Storage
from choice import react
from scripting import Scripting
from fatfox import FatFox

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
	filename = "orakel.cfg"
	config = configparser.SafeConfigParser()
	config.read(filename)

	jid = config.get("xmpp", "jid")
	password = config.get("xmpp", "password")
	room = config.get("xmpp", "room")
	nick = config.get("xmpp", "nick")

	logging.basicConfig(level=logging.INFO,
		                        format='%(levelname)-8s %(message)s')

	storage = Storage(config.get("db", "storage"))

	questions = load_database(config.get("db", "questions"))
	msgdb = MessageDatabase(questions)
	pingpong = PingPong()
	alphabet = Alphabet()
	count = Count()
	greet = Greet([ x.strip() for x in
			config.get("modules", "greetings").split(",") ], nick)

	search_engines = load_database(config.get("db", "searchengines"))
	search = Search(search_engines)
	#expression = Expression()
	actions = Actions(storage)
	scripting = Scripting(storage, search_engines=search_engines)
	fatfox = FatFox()

	xmpp = Client(jid, password, room, nick)
	xmpp.register_plugin('xep_0030') # Service Discovery
	xmpp.register_plugin('xep_0045') # Multi-User Chat
	xmpp.register_plugin('xep_0199') # XMPP Ping
	xmpp.add_mentation_listener(msgdb)
	xmpp.add_mentation_listener(actions.active)
	xmpp.add_message_listener(pingpong)
	xmpp.add_message_listener(alphabet)
	xmpp.add_message_listener(count)
	xmpp.add_message_listener(search)
	xmpp.add_message_listener(greet)
	#xmpp.add_message_listener(expression)
	xmpp.add_message_listener(fatfox)
	xmpp.add_message_listener(actions.passive)
	xmpp.add_message_listener(react)
	xmpp.add_message_listener(scripting)

	if xmpp.connect():
		xmpp.process(block=True)
	else:
		print("Unable to connect")
