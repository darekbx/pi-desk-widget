import requests
import json

from bs4 import BeautifulSoup
from datetime import datetime
import csv

from storage import Storage

class Covid19():
	WORLDOMETER = "https://www.worldometers.info/coronavirus"

	def load(self):
		storage = Storage()
		storage.connect()
		rows = storage.fetch()
		storage.close()
		return rows

	def refresh(self):
		storage = Storage()
		storage.connect()

		response = requests.get(self.WORLDOMETER, timeout = 30)

		soup = BeautifulSoup(response.text, 'html.parser')
		main_table = soup.find(id='main_table_countries_today')
		
		today = datetime.today()
		rows = main_table.find_all('tr')[1:]
		data = []

		for row in rows:
			tr = row.find('tr')
			items = row.find_all('td')
			country = items[0].text

			total_cases = items[1].text
			total_deaths = items[3].text
			total_recovered = items[5].text
			active_cases = items[6].text
			critical_cases = items[7].text
			
			data.append({
				'area': country,
				'total_cases': self.format_int(total_cases),
				'total_deaths': self.format_int(total_deaths),
				'total_recovered': self.format_int(total_recovered),
				'active_cases': self.format_int(active_cases),
				'critical_cases': self.format_int(critical_cases),
				'year': today.year,
				'month': today.month,
				'day': today.day
			})

		total_cases = data[-1]
		total_cases.update({'area': 'Total'})
		storage.add(total_cases)
		poland_cases = list(filter(lambda item: item['area'] == 'Poland', data))

		if len(poland_cases) == 1:
			storage.add(poland_cases[0])

		storage.close()

	def format_int(self, value):
		value = value.rstrip()
		if len(value) == 0:
			return 0
		return int(value.replace(',', '').replace('+', ''))

if __name__ == "__main__":
	covid19 = Covid19()
	covid19.refresh()
	covid19.load()