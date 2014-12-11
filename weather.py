# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import requests
from time import time

class Weather(object):
	def __init__(self, storage, config, weather):
		self.storage = storage
		self.config = config
		self.weather = weather
		try:
			self.storage['lastweather']
		except:
			self.storage['lastweather'] = 0

	def action(self, msg, send_message):
		try:
			print(msg.lower())
			if "!wetter" in msg.lower() or "!weather" in msg.lower():
				data = msg.split(' ')
				print(len(data))
				if len(data) == 2:
					api_url = 'http://api.openweathermap.org/data/2.5/weather?q='+data[1]+'&units=metric&lang=de'
					r = requests.get(api_url)
					json =  r.json()
					cod = str(json['cod'])
					temp = str(json['main']['temp'])
					description = json['weather'][0]['description']
					if cod == '404':
						send_message('Keine Wetterdaten gefunden')
					else:
						send_message('Es hat '+temp+'°C und ist '+description)
				elif len(data) == 3:
					print(len(data))
					api_url = 'http://api.openweathermap.org/data/2.5/forecast/daily?q='+data[1]+'&mode=json&units=metric&lang=de&cnt='+data[2]
					r = request.get(api_url)
					json = r.json()
					cod = str(json['cod'])
					day = json['list'][-1]
					tmin = str(day['temp']['min'])
					tmax = str(day['temp']['max'])
					description = day['description']
					send_message('In '+data[2]-1+' Tagen wird es minimal '+tmin+'°C und maximal '+tmax+'°C haben. Es wird '+description+' sein')
				else:
					send_message('Falsches Format')

			return True
		except:
			return False

	def __call__(self, msg, nick, send_message):
		t = time()
		if (t - self.storage['lastweather']) < \
				self.config.getint("timeouts", "weather"):
			return False
		if not self.action(msg, send_message):
			return False
		self.storage['lastweather'] = t
		return True
