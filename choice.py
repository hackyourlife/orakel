# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import re
from utils import oneof

def choice(s):
	r = r'^((hm+)?\.*\s+|.*:\s+)?([\sa-zA-ZäöüÄÖÜß-]+)\soder\s([\sa-zA-ZäöüÄÖÜß-]+)\?'
	match = re.match(r, s)
	if match:
		print(match.groups())
		return [ match.group(3), match.group(4) ]
	r = r'((hm+)?\.*\s+|.*:\s+)?([\sa-zA-ZäöüÄÖÜß-]+(,\s[\sa-zA-ZäöüAÖÜß-]+)+,?\soder\s[\sa-zA-ZäöüÄÖÜß-]+)\?'
	match = re.match(r, s)
	if match:
		data = [ x.strip() for x in match.group(3).split(",") ]
		fields = data[:-1] + [ x.strip()
				for x in data[-1].split("oder ")
				if len(x.strip()) > 0 ]
		return fields
	return None

def react(msg, nick, send_message):
	choices = choice(msg.strip())
	if choices:
		send_message(oneof(choices))
		return True
	return False
