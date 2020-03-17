import requests
import json

from datetime import datetime
import csv

class Covid19():
	ARGS = "?f=json&where=1=1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&resultOffset=0&resultRecordCount=100&cacheHint=true"
	URL = "https://services1.arcgis.com/YmCK8KfESHdxUQgm/arcgis/rest/services/KoronawirusPolska_czas/FeatureServer/0/query"

	ALTERNATIVE_URL = "http://covid.sikorski.pw/data/cov.csv"

	def load(self):
		return self.load_alternate()

	def load_alternate(self):
		response = requests.get(self.ALTERNATIVE_URL, timeout = 30)
		out = []
		for index, line in enumerate(response.text.split('\r\n')):
			if index == 0:
				continue
			if len(line) < 5:
				continue

			chunks = line.split(',')
			full_date = chunks[0]
			date = full_date.split(" ")[0]

			if len(out) > 1 and out[-1]['date'] == date:
				out[-1].update({
					'cases': int(chunks[1]), 
					'deaths': int(chunks[2])
				}) 
			else:
				out.append({ 
					'date': date, 
					'cases': int(chunks[1]), 
					'deaths': int(chunks[2]), 
					'healed': -1,
				})
		
		return out

	def load_arcgis(self):
		response = requests.get(self.URL + self.ARGS, timeout = 30)
		data = json.loads(response.text)

		out = []
		
		for row in data['features']:
			date = self.toDate(row['attributes']['Aktualizacja'])
			out.append({ 
				'date': date, 
				'cases': row['attributes']['Potwierdzone'], 
				'deaths': row['attributes']['Smiertelne'], 
				'healed': row['attributes']['Wyleczone'],
			})
		
		return out

	def toDate(self, value):
		return datetime.utcfromtimestamp(int(value / 1000)).strftime('%Y-%m-%d')
