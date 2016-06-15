# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import requests
import re
from lxml import etree
from io import StringIO
from module import Module, PRIVMSG

# extend 'Module' to get all the useful functions
class Weather(Module):
	def __init__(self, **keywords):
		# register for private messages only
		super(Weather, self).__init__([PRIVMSG], name=__name__,
				**keywords)

	def get_weather(self):
		try:
			response = requests.get('http://www.meteo.physik.uni-muenchen.de/dokuwiki/doku.php?id=wetter:garching:neu')
			html = str(response.content)
			parser = etree.HTMLParser()
			tree = etree.parse(StringIO(html), parser)

			#dictionary/array
			values = [ re.sub(r'\s+', ' ', x.strip()) for x in tree.xpath('//table[@border="1"]/tr/td/text()') ]

			return "Es hat auf %s, %s bei %s Luftfeuchtigkeit und die Windgeschwindigkeit beträgt %s" % \
					(values[3], values[12], values[39], values[48])
		except Exception as e:
			# there is a central logging infrastructure
			self.do_log("Exception caught: %s" % str(e))

	# override the callback method to handle incoming messages
	def private_msg(self, jid, msg):
		if msg == "weather": # if someone sent 'weather'...
			weather = self.get_weather()
			self.send_private(jid, weather) # ... send the weather
