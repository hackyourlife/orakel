# vim:set ts=8 sts=8 sw=8 tw=80 noet:

import re	
from utils import oneof

class Cookies(object):
	def __call__(self, msg, nick, send_message):
		if msg.lower().startswith("keks"):
			result = self.handle(msg, nick)
		else:
			return False

		if result:
			send_message(result)
			return True

		return False
 
	def handle(self, msg, nick):
		users = ["Socke", "Malte", "Fatfox", "Schneck", "SchinkiBa",
				"T", "tchab", "Koch", "Hacki", "willi", "allen", nick]
 
		cookies = ["Bier", "Brownie", "Steak", "Club-Sandwich",
				"Energy-Drink", "Regenbogen", "Burger", "Wein", "Vanille", 
				"Lima", "Wolken", "Schoko", "Erdbeer", "Veggie" ]
 
		r = r'(?i)^keks für (\w+)!?$'
		match = re.match(r, msg)
 
		if match:
			users = [match.group(1)]
		elif msg.lower() != 'keks?':
			return False

		return "/me gibt %s einen %s-Keks." % (oneof(users),
				oneof(cookies))
