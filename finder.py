# vim:set ts=8 sts=8 sw=8 tw=80 noet:

import pypygo

class Finder(object):
	def __call__(self, msg, nick, send_message):
		if "!find " in msg.lower():
			result = self.finder(msg, nick)
		else:
			return False

		if result:
			send_message(result)
			return True

		return False


	def finder(self, msg, nick):
		result = ""
		try:
			question = pypygo.query(msg[6:])
			result = question.abstract_text[0:100] + "... [" +question.abstract_url + "]"
		except ConnectionError:
			result = "Keine Verbindung zu duckduckgo möglich."
		finally:
			if len(result) < 1:
				result = "Ich konnte leider nichts finden. :("
			return(result)

