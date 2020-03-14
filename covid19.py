import requests
import json

from datetime import datetime

class Covid19():

	URL = "https://services1.arcgis.com/YmCK8KfESHdxUQgm/arcgis/rest/services/KoronawirusPolska_czas/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=ObjectId%2CPotwierdzone%2CAktualizacja&orderByFields=Aktualizacja%20asc&resultOffset=0&resultRecordCount=2000&cacheHint=true"

	def load(self):
		response = requests.get(self.URL)
		data = json.loads(response.text)

		out = []

		for row in data['features']:
			date = self.toDate(row['attributes']['Aktualizacja'])
			out.append({ 'date': date, 'cases': row['attributes']['Potwierdzone']})
		
		return out

	def toDate(self, value):
		return datetime.utcfromtimestamp(int(value / 1000)).strftime('%Y-%m-%d')
