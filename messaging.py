# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import sys
import configparser
import pika
import threading
import queue

if sys.version_info < (3, 0):
	reload(sys)
	sys.setdefaultencoding('utf8')

ROUTING_KEY_PRESENCE		= "presence"
ROUTING_KEY_MUC			= "mucmsg"
ROUTING_KEY_MUC_MENTION		= "mucmentionmsg"
ROUTING_KEY_SENDMUC		= "sendmuc"
ROUTING_KEY_PRIVMSG		= "privmsg"
ROUTING_KEY_SENDPRIVMSG		= "sendprivmsg"
ROUTING_KEY_LOG			= "log"
ROUTING_KEY_CONFIG		= "config"
ROUTING_KEY_COMMAND		= "command"

ROUTING_KEYS = [ROUTING_KEY_PRESENCE, ROUTING_KEY_MUC, ROUTING_KEY_MUC_MENTION,
		ROUTING_KEY_SENDMUC, ROUTING_KEY_PRIVMSG,
		ROUTING_KEY_SENDPRIVMSG, ROUTING_KEY_LOG, ROUTING_KEY_CONFIG,
		ROUTING_KEY_COMMAND]

def open_connection(on_open=None):
	filename = "orakel.cfg"
	config = configparser.SafeConfigParser()
	config.read(filename)

	hostname = config.get("messaging", "hostname")
	exchange = config.get("messaging", "exchange")
	virtual_host = None
	port = None
	username = None
	password = None
	heartbeat = 30
	try:
		port = config.getint("messaging", "port")
	except configparser.NoOptionError: pass
	except TypeError: pass
	except KeyError: pass
	try:
		heartbeat = config.getint("messaging", "heartbeat")
	except configparser.NoOptionError: pass
	except TypeError: pass
	except KeyError: pass
	try:
		username = config.get("messaging", "username")
		password = config.get("messaging", "password")
	except KeyError: pass

	parts = ["amqp://"]
	if not username is None and not password is None:
		parts += ["%s:%s@" % (username, password)]
	parts += [hostname]
	if not port is None:
		parts += [":%d" % port]
	parts += ["/"]
	if not virtual_host is None:
		parts += [virtual_host]
	querystring = ["heartbeat_interval=%d" % heartbeat]
	qs = "&".join(querystring)
	url = "".join(parts)
	if len(qs) > 0:
		url += "?" + qs

	connection = None
	if on_open:
		connection = pika.SelectConnection(pika.URLParameters(url),
				on_open_callback=on_open)
	else:
		connection = pika.BlockingConnection(pika.URLParameters(url))

	return connection, exchange

# Synchronization for pika
class Sender(object):
	def __init__(self, channel, exchange):
		self.channel = channel
		self.exchange = exchange
		self.queue = queue.Queue()
		self.running = True

	def send(self, body, routing_key):
		self.queue.put({'body': body, 'routing_key': routing_key})

	def stop(self):
		self.running = False
		self.queue.join()

	def start(self):
		def worker():
			while self.running or not self.queue.empty():
				msg = self.queue.get()
				self.channel.basic_publish(
						exchange=self.exchange,
						routing_key=msg['routing_key'],
						body=msg['body'])
				self.queue.task_done()
		t = threading.Thread(target=worker)
		t.daemon = True
		t.start()
