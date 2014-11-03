# vim:set ts=8 sts=8 sw=8 tw=80 noet:

import re
import socket
import urllib.request
from bs4 import BeautifulSoup
from multiprocessing import Process

class Urltitle(object):
	def __init__(self):
		self.buffer = ['Keine URL gespeichert.'] 
	def __call__(self, msg, nick, send_message):
		if "http" in msg.lower():
			result = self.save_url(msg, nick)
		elif "!titel" == msg.strip():
			result = self.output_url(msg, nick)
		else:
			return False

		if result:
			send_message(result)
			return True

		return False

	def save_url(self, msg, nick):
		self.buffer = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+[^http]', msg)

		return False

	def output_url(self, msg, nick):
		url_array = []
		try:
			try:
				url = urllib.request.urlopen(self.buffer[0],None, 5)
				meta = url.info()
				print(meta)
				website = url.read()
				bs = BeautifulSoup(website)
				return bs.find('title').text
			except socket.timeout:
				return '** TIMEOUT **'

		except ValueError:
			return "Keine URL gespeichert." 
		
		finally: 
			self.buffer = ['Keine URL gespeichert.'] 

		return False 
