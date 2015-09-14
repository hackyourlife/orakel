# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import requests
from urllib.parse import quote as urlencode
from module import Module, CONFIG, COMMAND

class Weather(Module):
	def __init__(self, **keywords):
		super(Weather, self).__init__([CONFIG, COMMAND], name=__name__,
				**keywords)

	def get_weather(self, location, days=0):
		encoded = urlencode(location)
		no_data = "Keine Wetterdaten gefunden"
		try:
			if days > 0:
				api_url = "http://api.openweathermap.org/data/"\
						"2.5/forecast/daily?q=%s" \
						"&mode=json&units=metric" \
						"&lang=de&cnt=%d" % \
								(encoded, days)
				r = requests.get(api_url)
				json = r.json()
				cod = json['cod']
				day = json['list'][-1]
				tmin = str(day['temp']['min'])
				tmax = str(day['temp']['max'])
				description = day['description']
				if cod == 404:
					return no_data
				return "In %d Tagen wird es minimal %2f°C und" \
						" maximal %2f°C haben." \
						" Es wird %s sein" % (days,
								tmin, tmax)
			else:
				api_url = "http://api.openweathermap.org/data/"\
						"2.5/weather?q=%s" \
						"&units=metric&lang=de"
				r = requests.get(api_url)
				json =  r.json()
				cod = json['cod']
				temp = json['main']['temp']
				description = json['weather'][0]['description']
				if cod == 404:
					return no_data
				return "Es hat %2f°C und ist %s" % \
						(temp, description)
		except Exception as e:
			self.log("Exception caught: %s" % str(e))
