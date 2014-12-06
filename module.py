# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import json
import logging
import traceback
import messaging

MUC = 0
MUC_MENTION = 1
PRIVMSG = 2

_MAPPING = [messaging.ROUTING_KEY_MUC, messaging.ROUTING_KEY_MUC_MENTION,
		messaging.ROUTING_KEY_PRIVMSG]

log = logging.getLogger(__name__)

class Log(object):
	def __init__(self, name, send):
		self.name = name
		self.send = send

	def log(self, severity, msg):
		self.send(msg, severity, self.name)

	def debug(self, msg):
		self.log('DEBUG', msg)

	def info(self, msg):
		self.log('INFO', msg)

	def warn(self, msg):
		self.log('WARN', msg)

	def error(self, msg):
		self.log('ERROR', msg)

	def critical(self, msg):
		self.log('CRITICAL', msg)

	def fatal(self, msg):
		self.log('FATAL', msg)

class Module(object):
	def __init__(self, topics=[], parent=None, name=None):
		self.parent = parent
		self.listeners = []
		self.topics = []
		self.name = __name__ if name is None else name
		self.log = Log(self.name, self.do_log)
		if parent:
			parent.register(self, topics)
			return

		self.connection, self.exchange = messaging.open_connection()
		self.channel = self.connection.channel()
		self.channel.exchange_declare(exchange=self.exchange,
				type="direct")

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
			if routing_key == messaging.ROUTING_KEY_MUC_MENTION:
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
		self.command('kick', data)

	def set_role(self, nick, role):
		data = {'nick': nick, 'role': role}
		self.command('set_role', data)

	def command(self, cmd, data):
		args = {'cmd': cmd}
		for key in data.keys():
			args[key] = data[key]
		self.send(messaging.ROUTING_KEY_COMMAND, args)

	def send_private(self, jid, msg):
		self.send(messaging.ROUTING_KEY_SENDPRIVMSG,
				{'to': jid, 'msg': msg})

	def do_log(self, msg, severity='INFO', module=None):
		if module is None:
			module = __name__
		self.send(messaging.ROUTING_KEY_LOG,
				{'severity': severity, 'module': module,
					'msg': msg})

	def send(self, key, data):
		if self.parent:
			self.parent.send(key, data)
			return
		self.channel.basic_publish(exchange=self.exchange,
				routing_key=key,
				body=json.dumps(data).encode('utf-8'))

	def start(self):
		self.channel.start_consuming()

	def stop(self):
		self.connection.close()

	# override those functions
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
			listener.private_msg(jid, msg)
