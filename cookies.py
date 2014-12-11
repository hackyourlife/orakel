# vim:set ts=8 sts=8 sw=8 tw=80 noet:

import re
import datetime
from utils import oneof
from module import Module, MUC

class Cookies(Module):
	def __init__(self, **keywords):
		super(Cookies, self).__init__([MUC], name=__name__, **keywords)

	def muc_msg(self, msg, nick, **keywords):
		if "keks" in msg.lower():
			result = self.handle(msg, nick)
			if result:
				self.send_muc(result)

	def handle(self, msg, nick):
		users = ["Socke", "Malte", "Fatfox", "Schneck", "thomasba", "T",
				"tchab", "Koch", "Hacki", "willi", "allen",
				nick]

		cookies = ["Bier", "Brownie", "Steak", "Club-Sandwich",
				"Energy-Drink", "Regenbogen", "Burger", "Wein",
				"Vanille", "Lima", "Wolken", "Schoko",
				"Erdbeer", "Veggie", "Cola", "Limo",  "Karamel",
				"Ananas", "Schinken", "Kaffee", "Koffein"]


		now = datetime.datetime.now()

		if now.month == 12:
			cookies += ["Weihnachts", "Zimt"]
		elif now.month == 10:
			cookies += ["Kürbis"]
		elif now.month == 4:
			cookies += ["Osterhasen", "Lamm"]

		if now.hour >= 16 or now.weekday() >= 4:
			cookies += ["Bier", "Bier", "Bier"]

		r = r'(?i)^([a-z-]+-)?keks für (\w+)(!|\?)?$'
		match = re.match(r, msg)

		if match:
			users = [match.group(2)]
			if match.group(2) == "tchab":
				cookies = ["Regenbogen", "Wurst"]
			elif match.group(2) in ["sonok", "snook", "Socke"]:
				cookies = ["Nudel", "Ketchup", "Nudel-Ketchup"]
			elif match.group(2) in ["c143", "tse143", "tse", "c143po"]:
				cookies = ["Bier", "Pizza", "Kartoffel", "Tofu",
						"Salat", "Imaginären"]
			if not match.group(1) is None:
				cookie = match.group(1)[:-1].split('-')
				cookie = [x[0].upper() + x[1:].lower() \
						for x in cookie]
				cookies = [ "-".join(cookie) ]
			if match.group(3) == '?':
				return 'nein!'
		elif not msg.lower() in ['keks', 'keks?', 'keks!']:
			return False

		return "/me gibt %s einen %s-Keks." % (oneof(users),
				oneof(cookies))
