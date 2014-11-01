# vim:set ts=8 sts=8 sw=8 tw=80 noet:

import re
import urllib.request
from bs4 import BeautifulSoup

class Urltitle(object):
	def __init__ (self, storage):
		self.storage = storage
		self.muted = storage['last_urls']
		self.storage['last_urls'] = [] 

	def __call__(self, msg, nick, send_message):
		if "http" in msg.lower():
			result = self.save_url(msg, nick)
		elif "!titel" in msg.lower():
			result = self.output_url(msg, nick)
		else:
			return False

		if result:
			send_message(result)
			return True

		return False

	def save_url(self, msg, nick):
		try:
			url_array = []
			urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+[^http]', msg)

			for index, url in enumerate(urls):
				url = urllib.request.urlopen(url)
				website = url.read()
				bs = BeautifulSoup(website)

				url_array.append(bs.find('title').text)
		except urllib.error.HTTPError:
			return False
		finally:
			self.storage['last_urls'] = url_array

		return False

	def output_url(self, msg, nick):
		try:
			saved_urls = self.storage['last_urls']

			if len(saved_urls) < 2:
				return saved_urls[0]
			else:
				return ', '.join(saved_urls)
		finally: self.storage['last_urls'] = []

		return False
