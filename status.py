# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

class Status(object):
	def __getattr__(self, name):
		if name == 'participants':
			return self.get_participants()
		if name == 'online':
			online = self.get_participants()
			return [ online[x]['nick'] for x in online ]

	def show_participants(self, *args, **keywords):
		if len(args) != 0:
			return
		send_message = keywords['send_message']
		participants = self.participants
		send_message("participants: %s" % ", ".join(
				[ participants[x]['nick'] \
						for x in participants ]))

	def show_online_users(self, *args, **keywords):
		if len(args) != 0:
			return
		send_message = keywords['send_message']
		send_message("online: %s" % ", ".join(self.online))
