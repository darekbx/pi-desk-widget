import requests
import json

from bs4 import BeautifulSoup
from datetime import datetime
import csv

class Covid19():
	WORLDOMETER = "https://www.worldometers.info/coronavirus"

	def load(self):
		return self.load_sikorski()

	def load_worldometer(self):
		response = requests.get(self.WORLDOMETER, timeout = 30)

		soup = BeautifulSoup(response.text, 'html.parser')
		main_table = soup.find(id='main_table_countries_today')
		
		rows = main_table.find_all('tr')[1:]
		data = []

		for row in rows:
			tr = row.find('tr')
			items = row.find_all('td')
			country = items[0].text

			total_cases = items[1].text
			new_cases = items[2].text

			total_deaths = items[3].text
			new_deaths = items[4].text

			total_recovered = items[5].text
			critical_cases = items[7].text
			
			data.append({
				'country': country,
				'total_cases': self.format_int(total_cases),
				'new_cases': self.format_int(new_cases),
				'total_deaths': self.format_int(total_deaths),
				'new_deaths': self.format_int(new_deaths),
				'total_recovered': self.format_int(total_recovered),
				'critical_cases': self.format_int(critical_cases)
			})

		total_cases = data[-1]
		poland_cases = list(filter(lambda item: item['country'] == 'Poland', data))

		if len(poland_cases) == 1:
			print(poland_cases)

	def format_int(self, value):
		value = value.rstrip()
		if len(value) == 0:
			return 0
		return int(value.replace(',', '').replace('+', ''))

Covid19().load_worldometer()