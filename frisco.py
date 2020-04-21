import requests
import brotli
import json
import datetime as dt
from dateutil.parser import parse

class FriscoDeliveryObserver:

	credentials_file = 'frisco_credentials'
	token_url = 'https://commerce.frisco.pl/connect/token'
	delivery_url = 'https://commerce.frisco.pl/api/users/745598/calendar/Van'

	def authorize(self):
		token_headers = {
			'Referer': 'https://www.frisco.pl/',
			'Accept': 'application/json',
			'Accept-Encoding': 'gzip, deflate, br',
			'X-Frisco-Visitorid': self.get_property('visitor-id')
		}
		data = {
			'username': self.get_property('username'),
			'password': self.get_property('password'),
			'grant_type': 'password'
		}

		token_response = requests.post(self.token_url, data=data, headers=token_headers)

		if token_response.status_code == 200:
			tokenJsonString = brotli.decompress(token_response.content)
			tokenJson = json.loads(tokenJsonString)
			return None, tokenJson['access_token']
		else:
			return "Token error: {0}".format(token_response.text), None
	
	def get_delivery_data(self, auth_token):
		headers = { 
			'Accept': 'application/json',
			'Accept-Encoding': 'gzip, deflate, br',
			'X-Frisco-Division': self.get_property('division'),
			'X-Frisco-Features': 'BalanceAmount=1',
			'X-Frisco-Visitorid': self.get_property('visitor-id'),
			'Authorization': 'Bearer {0}'.format(auth_token) 
		}
		response = requests.get(self.delivery_url, headers=headers)
		if response.status_code == 200:
			jsonString = brotli.decompress(response.content)
			content = json.loads(jsonString)
			newest_delivery_date = content['firstOpenWindow']['deliveryWindow']['startsAt']
			dt = parse(newest_delivery_date)
			parsed_date = dt.strftime('%Y-%m-%d %H:%M')
			return parsed_date
		else:
			return "Token error: {0}".format(response.status_code), None

	def get_property(self, key):
		with open(self.credentials_file, "r") as handle:
			data = json.load(handle)
			return data[key]

if __name__ == "__main__":
	frisco = FriscoDeliveryObserver()
	error, auth_token = frisco.authorize()
	if error is None:
		delivery_date = frisco.get_delivery_data(auth_token)
		print(delivery_date)
	else:
		print(error)
