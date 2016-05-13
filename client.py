# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import sleekxmpp
from sleekxmpp.xmlstream import ET
from time import time
import logging


class Client(sleekxmpp.ClientXMPP):
	mention_listeners = []
	private_listeners = []
	message_listeners = []
	online_listeners = []
	offline_listeners = []
	init_complete_listeners = []
	participants = {}

	def __init__(self, jid, password, room, nick, log=None):
		sleekxmpp.ClientXMPP.__init__(self, jid, password)

		self.room = room
		self.nick = nick
		self.online = False

		if not log is None:
			self.log = log
			self.log.name = __name__
		else:
			self.log = logging.getLogger(__name__)

		self.add_event_handler("session_start", self.start)
		self.add_event_handler("groupchat_message", self.muc_message)
		self.add_event_handler("message", self.message)
		self.add_event_handler("muc::%s::got_online" % self.room,
				self.muc_online)
		self.add_event_handler("muc::%s::got_offline" % self.room,
				self.muc_offline)

	def add_mention_listener(self, listener):
		self.mention_listeners += [ listener ]

	def add_message_listener(self, listener):
		self.message_listeners += [ listener ]

	def add_online_listener(self, listener):
		self.online_listeners += [ listener ]

	def add_offline_listener(self, listener):
		self.offline_listeners += [ listener ]

	def add_private_listener(self, listener):
		self.private_listeners += [ listener ]

	def add_init_complete_listener(self, listener):
		self.init_complete_listeners += [ listener ]

	def start(self, event):
		self.get_roster()
		self.send_presence()
		self.plugin['xep_0045'].joinMUC(self.room, self.nick, wait=True)

	def muc_message(self, msg):
		nick = msg['mucnick']
		jid = msg['from'].full
		role = None
		affiliation = None
		if len(nick) != 0:
			jid = self.plugin['xep_0045'].getJidProperty(self.room,
					nick, 'jid')
			try:
				jid = jid.full
			except:
				jid = ""
			if len(jid) == 0:
				jid = msg['from'].full
			role = self.plugin['xep_0045'].getJidProperty(self.room,
					nick, 'role')
			affiliation = self.plugin['xep_0045'].getJidProperty(
					self.room, nick, 'affiliation')
		if nick != self.nick:
			if not self.online:
				return
			if len(msg['body']) == 0:
				return
			if msg['body'].startswith(self.nick):
				if len(msg['body']) <= len(self.nick) + 2:
					return
				text = msg['body'][len(self.nick) + 1:].strip()
				for listener in self.mention_listeners:
					listener(msg=text, nick=nick, jid=jid,
							role=role,
							affiliation=affiliation)
			else:
				for listener in self.message_listeners:
					listener(msg=msg['body'], nick=nick,
							jid=jid, role=role,
							affiliation=affiliation)

	def message(self, msg):
		if msg['type'] in ('chat', 'normal'):
			text = msg['body']
			jid = msg['from'].full
			if len(text) == 0:
				return
			self.log.info("[PRIVATE] %s: '%s'" % (jid, text))
			for listener in self.private_listeners:
				listener(msg=text, jid=jid)

	def muc_online(self, presence):
		if presence['muc']['nick'] != self.nick:
			jid = presence['from'].full
			fulljid = jid
			if len(presence['muc']['jid'].full):
				fulljid = presence['muc']['jid'].full
			role = presence['muc']['role']
			nick = presence['muc']['nick']
			affiliation = presence['muc']['affiliation']
			self.participants[jid] = {'jid': fulljid,
					'role': role,
					'nick': nick,
					'affiliation': affiliation,
					'time': time()}
			self.log.info("online: %s: %s [%s]" % (fulljid, role,
					nick))
			if not self.online:
				return
			for listener in self.online_listeners:
				listener(jid=fulljid, nick=nick, role=role,
						affiliation=affiliation,
						localjid=jid)
		else:
			for listener in self.init_complete_listeners:
				listener()
			self.online = True

	def muc_offline(self, presence):
		if presence['muc']['nick'] != self.nick:
			jid = presence['from'].full
			nick = self.participants[jid]['nick']
			fulljid = self.participants[jid]['jid']
			del self.participants[jid]
			self.log.info("offline: %s: %s" % (fulljid, nick))
			for listener in self.offline_listeners:
				listener(jid=fulljid, nick=nick)

	def muc_send(self, msg):
		sleekxmpp.ClientXMPP.send_message(self, mto=self.room,
				mbody=msg, mtype='groupchat')

	def msg_send(self, to, msg, muc):
		jid = to
		if muc:
			jid = "%s/%s" % (self.room, to)
		sleekxmpp.ClientXMPP.send_message(self, mto=jid, mbody=msg,
				mtype='chat')

	def set_role(self, nick, role):
		if not self.is_participant(nick):
			self.log.warn("trying to change role of non-existent" \
					" user '%s'" % nick)
			return False
		self.log.info("setting role for %s to %s" % (nick, role))
		return self.plugin['xep_0045'].setRole(self.room, nick, role)

	def kick(self, nick, reason=None):
		if not self.is_participant(nick):
			self.log.warn("trying to kick non-existent user '%s'" %
					nick)
			return False
		pr = "no reason" if reason is None else "reason: %s" % reason
		self.log.info("kicking %s (%s)" % (nick, pr))
		query = ET.Element("{http://jabber.org/protocol/muc#admin}query")
		item = ET.Element("item", {"role": "none", "nick": nick})
		if not reason is None:
			rxml = ET.Element("reason")
			rxml.text = reason
			item.append(rxml)
		query.append(item)
		iq = self.makeIqSet(query)
		iq['to'] = self.room
		result = iq.send()
		if result is False or result['type'] != 'result':
			raise ValueError
		return True

	def is_participant(self, nick):
		return not self.get_participant(nick) is None

	def get_participant(self, nick):
		for jid in self.participants:
			participant = self.participants[jid]
			if participant["nick"] == nick:
				return participant
		return None

	def get_participants(self):
		return self.participants
