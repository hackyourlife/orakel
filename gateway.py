#!/bin/python
# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import sys
import configparser
import json
import logging
import queue
import threading
import traceback

from messaging import open_connection, ROUTING_KEY_PRESENCE, ROUTING_KEY_MUC, \
		ROUTING_KEY_MUC_MENTION, ROUTING_KEY_SENDMUC, \
		ROUTING_KEY_PRIVMSG, ROUTING_KEY_SENDPRIVMSG, ROUTING_KEY_LOG, \
		ROUTING_KEY_COMMAND
from client import Client

log = logging.getLogger(__name__)

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

	def start(self):
		def worker():
			while self.running:
				msg = self.queue.get()
				self.channel.basic_publish(
						exchange=self.exchange,
						routing_key=msg['routing_key'],
						body=msg['body'])
				self.queue.task_done()
		t = threading.Thread(target=worker)
		t.daemon = True
		t.start()

xmpp = None
if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO,
		                        format='%(levelname)-8s %(message)s')

	connection, exchange = open_connection()
	channel = connection.channel()
	channel.exchange_declare(exchange=exchange, type="direct")

	# ugly workaround because pika does not like multiple threads
	send_connection, exchange = open_connection()
	send_channel = send_connection.channel()
	sender = Sender(send_channel, exchange)
	sender.start()

	def send(key, data):
		sender.send(routing_key=key,
			body=json.dumps(data).encode('utf-8'))

	def receive(ch, method, properties, body):
		routing_key = method.routing_key
		data = json.loads(body.decode('utf-8'))
		#print("[<=] %r:%r" % (method.routing_key, data))
		try:
			if routing_key == ROUTING_KEY_SENDMUC:
				xmpp.muc_send(data)
			elif routing_key == ROUTING_KEY_SENDPRIVMSG:
				xmpp.msg_send(data['to'], data['msg'])
			elif routing_key == ROUTING_KEY_COMMAND:
				cmd = data['cmd']
				if cmd == 'kick':
					nick = data['nick']
					reason = data['reason'] \
							if 'reason' in data \
							else None
					xmpp.kick(nick, reason)
				elif cmd == 'set_role':
					nick = data['nick']
					role = data['role']
					xmpp.set_role(nick, role)
				else:
					log.warn("unknown command '%s'" % cmd)
			elif routing_key == ROUTING_KEY_LOG:
				severity = data['severity']
				module = data['module']
				message = data['msg']
				if len(module) > 10:
					module = "%s..." % module[0:7]
				msg = "[%-10s] %s" % (module, message)
				if severity == 'DEBUG':
					log.debug(msg)
				elif severity == 'INFO':
					log.info(msg)
				elif severity == 'WARN':
					log.warn(msg)
				elif severity == 'ERROR':
					log.error(msg)
				elif severity == 'CRITICAL':
					log.critical(msg)
				elif severity == 'FATAL':
					log.fatal(msg)
		except KeyError as e:
			log.warn("missing key: %s (%s)" % (e, routing_key))
		except Exception as e:
			log.error("caught exception: %s" % e)
			traceback.print_exc()

	result = channel.queue_declare(exclusive=True)
	queue_name = result.method.queue
	for routing_key in [ROUTING_KEY_SENDMUC, ROUTING_KEY_SENDPRIVMSG,
			ROUTING_KEY_LOG, ROUTING_KEY_COMMAND]:
		channel.queue_bind(exchange=exchange, queue=queue_name,
				routing_key=routing_key)

	channel.basic_consume(receive, queue=queue_name, no_ack=True)

	filename = "orakel.cfg"
	config = configparser.SafeConfigParser()
	config.read(filename)
	jid = config.get("xmpp", "jid")
	password = config.get("xmpp", "password")
	room = config.get("xmpp", "room")
	nick = config.get("xmpp", "nick")

	xmpp = Client(jid, password, room, nick)
	xmpp.register_plugin('xep_0030') # Service Discovery
	xmpp.register_plugin('xep_0045') # Multi-User Chat
	xmpp.register_plugin('xep_0199') # XMPP Ping

	def muc_msg(msg, nick, jid, role, affiliation):
		send(ROUTING_KEY_MUC, {'nick': nick, 'jid': jid, 'role': role,
			'affiliation': affiliation, 'msg': msg})

	def muc_mention(msg, nick, jid, role, affiliation):
		send(ROUTING_KEY_MUC_MENTION, {'nick': nick, 'jid': jid, 'role':
			role, 'affiliation': affiliation, 'msg': msg})

	def priv_msg(msg, jid):
		send(ROUTING_KEY_PRIVMSG, {'jid': jid, 'msg': msg})

	def muc_online(jid, nick, role, affiliation):
		send(ROUTING_KEY_PRESENCE, {'type': 'online', 'jid': jid,
			'nick': nick, 'role': role, 'affiliation': affiliation})

	def muc_offline(jid, nick):
		send(ROUTING_KEY_PRESENCE, {'type': 'offline', 'jid': jid,
			'nick': nick})

	xmpp.add_message_listener(muc_msg)
	xmpp.add_mention_listener(muc_mention)
	xmpp.add_online_listener(muc_online)
	xmpp.add_offline_listener(muc_offline)
	xmpp.add_private_listener(priv_msg)

	if xmpp.connect():
		xmpp.process(block=False)
	else:
		print("Unable to connect")
		sys.exit(1)

	try:
		channel.start_consuming()
	except KeyboardInterrupt: pass

	sender.stop()
	xmpp.disconnect()
	connection.close()
	send_connection.close()
