# vim:set ts=8 sts=8 sw=8 tw=80 noet:

import pypygo

class Finder(object):
	def __call__(self, msg, nick, send_message):
		if "!find" in msg.lower():
			result = self.finder(msg, nick)
		else:
			return False

		if result:
			send_message(result)
			return True

		return False


	def finder(self, msg, nick):
		question = pypygo.query(msg[6:])
		print(question.abstract)
		return(question.abstract_url)

