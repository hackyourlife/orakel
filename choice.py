# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import re
from utils import oneof

def choice(s):
	r = r'^((hm+)?\.*\s+)?([a-zA-ZäöüÄÖÜß-]+)\soder\s([a-zA-ZäöüÄÖÜß-]+)\?'
	match = re.match(r, s)
	if match:
		print(match.groups())
		return [ match.group(3), match.group(4) ]
	r = r'((hm+)?\.*\s+|.*:\s+)?([a-zA-ZäöüÄÖÜß-]+(,\s[a-zA-ZäöüAÖÜß-]+)+\soder\s[a-zA-ZäöüÄÖÜß-]+)\?'
	match = re.match(r, s)
	if match:
		data = [ x.strip() for x in match.group(3).split(",") ]
		fields = data[:-1] + data[-1].split(" oder ")
		return fields
	return None

def react(msg, nick, send_message):
	choices = choice(msg.strip())
	if choices:
		send_message(oneof(choices))
		return True
	return False
