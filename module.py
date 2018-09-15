# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import json
import logging
import traceback
import messaging
from time import time as unixtime
from log import Log
from messaging import Sender

PRESENCE = 0
MUC = 1
MUC_MENTION = 2
PRIVMSG = 3
CONFIG = 4
COMMAND = 5

_MAPPING = [messaging.ROUTING_KEY_PRESENCE, messaging.ROUTING_KEY_MUC,
		messaging.ROUTING_KEY_MUC_MENTION,
		messaging.ROUTING_KEY_PRIVMSG, messaging.ROUTING_KEY_CONFIG,
		messaging.ROUTING_KEY_COMMAND]

log = logging.getLogger(__name__)

class Module(object):
	def __init__(self, topics=[], parent=None, name=None):
		self.parent = parent
		self.listeners = []
		self.topics = []
		self.name = __name__ if name is None else name
		self.participants = {}
		self.log = Log(self.name, self.do_log)
		if parent:
			parent.register(self, topics)
			return

		self.connection, self.exchange = messaging.open_connection()
		self.channel = self.connection.channel()
		self.channel.exchange_declare(exchange=self.exchange,
				exchange_type="direct")
		self.send_channel = self.connection.channel()
		self.send_channel.exchange_declare(exchange=self.exchange,
				exchange_type="direct")

		self.sender = Sender(self.send_channel, self.exchange)

		if len(topics) == 0:
			return

		self.register(topics=topics)

	def register(self, listener=None, topics=[]):
		no_topic = len(self.topics) == 0

		if not listener is None:
			self.listeners += [ listener ]

		if no_topic and len(topics) != 0:
			result = self.channel.queue_declare(exclusive=True)
			self.queue_name = result.method.queue

		for topic in topics:
			if topic in self.topics:
				continue
			self.topics += [ topic ]
			routing_key = _MAPPING[topic]
			self.channel.queue_bind(exchange=self.exchange,
					queue=self.queue_name,
					routing_key=routing_key)

		if no_topic and len(topics) != 0:
			self.channel.basic_consume(self.receive,
					queue=self.queue_name, no_ack=True)

	def receive(self, ch, method, properties, body):
		routing_key = method.routing_key
		data = json.loads(body.decode('utf-8'))
		try:
			if routing_key == messaging.ROUTING_KEY_PRESENCE:
				action = data['type']
				if action == "online":
					jid = data['jid']
					nick = data['nick']
					role = data['role']
					affiliation = data['affiliation']
					self.muc_online(jid=jid, nick=nick,
							role=role,
							affiliation=affiliation)
				elif action == "offline":
					jid = data['jid']
					nick = data['nick']
					self.muc_offline(jid=jid, nick=nick)
			elif routing_key == messaging.ROUTING_KEY_MUC_MENTION:
				nick = data['nick']
				jid = data['jid']
				role = data['role']
				affiliation = data['affiliation']
				msg = data['msg']
				self.muc_mention(nick=nick, jid=jid, role=role,
						affiliation=affiliation,
						msg=msg)
			elif routing_key == messaging.ROUTING_KEY_MUC:
				nick = data['nick']
				jid = data['jid']
				role = data['role']
				affiliation = data['affiliation']
				msg = data['msg']
				self.muc_msg(nick=nick, jid=jid, role=role,
						affiliation=affiliation,
						msg=msg)
			elif routing_key == messaging.ROUTING_KEY_PRIVMSG:
				jid = data['jid']
				msg = data['msg']
				self.private_msg(jid=jid, msg=msg)
			elif routing_key == messaging.ROUTING_KEY_CONFIG:
				key = data['key']
				value = data['value']
				self.config_change(key, value)
			elif routing_key == messaging.ROUTING_KEY_COMMAND:
				cmd = data['cmd']
				args = {key: data[key] for key in data
						if key != 'cmd'}
				if cmd == 'reload_config':
					self.reload_config()
				elif cmd == 'reconfigure_room':
					self.muc_reconfigure()
				else:
					self.command(cmd, **args)
			else:
				log.warn("unknown action: '%s'" % routing_key)

		except KeyError as e:
			log.warn("missing key: %s (%s)" % (e, routing_key))
		except Exception as e:
			log.error("caught exception: %s" % e)
			traceback.print_exc()

	def send_muc(self, msg):
		self.send(messaging.ROUTING_KEY_SENDMUC, msg)

	def kick(self, nick, reason=None):
		data = {'nick': nick}
		if reason:
			data['reason'] = reason
		self.send_cmd('kick', **data)

	def set_role(self, nick, role):
		data = {'nick': nick, 'role': role}
		self.send_cmd('set_role', **data)

	def send_cmd(self, cmd, **data):
		args = {'cmd': cmd}
		for key in data.keys():
			args[key] = data[key]
		self.send(messaging.ROUTING_KEY_COMMAND, args)

	def send_private(self, jid, msg, muc=False):
		self.send(messaging.ROUTING_KEY_SENDPRIVMSG,
				{'to': jid, 'msg': msg, 'muc': muc})

	def send_cfg(self, key, value):
		self.send(messaging.ROUTING_KEY_CONFIG,
				{'key': key, 'value': value})

	def do_log(self, msg, severity='INFO', module=None):
		if module is None:
			module = self.name
		self.send(messaging.ROUTING_KEY_LOG,
				{'severity': severity, 'module': module,
					'msg': msg})

	def send(self, key, data):
		if self.parent:
			self.parent.send(key, data)
			return
		self.sender.send(body=json.dumps(data).encode('utf-8'),
				routing_key=key)

	def start(self):
		for listener in self.listeners:
			listener.start()
		if self.parent:
			return
		self.sender.start()
		self.channel.start_consuming()

	def stop(self):
		for listener in self.listeners:
			listener.stop()
		if self.parent:
			return
		self.sender.stop()
		self.connection.close()

	# override those functions
	def muc_online(self, nick, jid, role, affiliation):
		self.participants[nick] = {'jid': jid, 'nick': nick,
				'role': role, 'affiliation': affiliation,
				'time': unixtime() }
		for listener in self.listeners:
			listener.muc_online(nick=nick, jid=jid, role=role,
					affiliation=affiliation)

	def muc_offline(self, nick, jid):
		del self.participants[nick]
		for listener in self.listeners:
			listener.muc_offline(nick=nick, jid=jid)

	def muc_mention(self, nick, jid, role, affiliation, msg):
		for listener in self.listeners:
			listener.muc_mention(nick=nick, jid=jid, role=role,
					affiliation=affiliation, msg=msg)

	def muc_msg(self, nick, jid, role, affiliation, msg):
		for listener in self.listeners:
			listener.muc_msg(nick=nick, jid=jid, role=role,
					affiliation=affiliation, msg=msg)

	def private_msg(self, jid, msg):
		for listener in self.listeners:
			listener.private_msg(jid=jid, msg=msg)

	def config_change(self, key, value):
		for listener in self.listeners:
			listener.config_change(key=key, value=value)

	def command(self, cmd, **args):
		try:
			if cmd == "room_info":
				data = args["participants"]
				participants = {}
				for jid in data:
					participant = data[jid]
					participants[participant["nick"]] = \
							participant
				self.participants = participants
		except Exception:
			pass

		for listener in self.listeners:
			listener.command(cmd, **args)

	def reload_config(self):
		for listener in self.listeners:
			listener.reload_config()

	def muc_reconfigure(self):
		for listener in self.listeners:
			listener.muc_reconfigure()
