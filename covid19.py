import requests
import json

from datetime import datetime

class Covid19():
	ARGS = "?f=json&where=1=1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&resultOffset=0&resultRecordCount=100&cacheHint=true"
	URL = "https://services1.arcgis.com/YmCK8KfESHdxUQgm/arcgis/rest/services/KoronawirusPolska_czas/FeatureServer/0/query"

	def load(self):
		response = requests.get(self.URL + self.ARGS)
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
