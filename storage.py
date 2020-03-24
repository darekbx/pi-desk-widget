import sqlite3
import os
from sqlite3 import Error
from datetime import datetime

class Storage:

	IS_DEBUG    = 'raspberrypi' not in os.uname()
	DB_NAME 	= "covid19.sqlite"
	LOCAL_PATH	= ''
	RPI_PATH	= '/home/pi/pi-display/'

	TABLE_DEFINITION = '''
CREATE TABLE IF NOT EXISTS entries (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	area TEXT,
	total_cases INTEGER,
	total_deaths INTEGER,
	total_recovered INTEGER,
	active_cases INTEGER,
	critical_cases INTEGER,
	year INTEGER,
	month INTEGER,
	day INTEGER
);
'''
	INSERT_DEFINITION = '''
INSERT INTO 
	entries 
VALUES
	(NULL, :area, :total_cases, :total_deaths, :total_recovered, :active_cases, :critical_cases, :year, :month, :day)
'''
	UPDATE_DEFINITION = '''
UPDATE 
	entries
SET	
	total_cases = ?, total_deaths = ?, total_recovered = ?, active_cases = ?, critical_cases = ?
WHERE
	area = ? AND year = ? AND month = ? AND day = ?
'''

	SELECT_QUERY = "SELECT * FROM entries ORDER BY year, month, day"

	connection 	= None
	
	def import_csv(self):
		self.connect()
		cursor = self.connection.cursor()		
		with open('cov.csv', 'r') as handle:
			lines = handle.readlines()[1:]
			for line in lines:
				line = line.rstrip()
				if len(line) < 2:
					continue
				chunks = line.split(',')
				date_object = datetime.strptime(chunks[0],
                           '%Y-%m-%d %H:%M:%S')
				year = date_object.year
				month = date_object.month
				day = date_object.day

				data = { 
					'area': 'Poland', 
					'total_cases': int(chunks[1]),
					'total_deaths': int(chunks[2]),
					'total_recovered': 0,
					'active_cases': 0,
					'critical_cases': 0,
					'year': year,
					'month': month,
					'day': day
				}

				cursor.execute(self.INSERT_DEFINITION, data)

		self.connection.commit()
		self.close()

	def connect(self):
		path = self.LOCAL_PATH if self.IS_DEBUG else self.RPI_PATH
		try:
			self.connection = sqlite3.connect(path + self.DB_NAME)
			if self.connection is not None:
				self._create_tables()
		except Error as e:
			print(e)

	def close(self):
		if self.connection:
			self.connection.close()

	def fetch(self):
		try:
			self.connection.row_factory = self.dict_factory
			cursor = self.connection.cursor()
			cursor.execute(self.SELECT_QUERY)
			result = cursor.fetchall()
			return result
		except Error as e:
			print(e)

	def add(self, data):
		try:
			cursor = self.connection.cursor()

			update_data = (
				# Fields to update
				data['total_cases'], data['total_deaths'], data['total_recovered'], data['active_cases'], data['critical_cases'],
				# Where args
				data['area'], data['year'], data['month'], data['day']
			)
			cursor.execute(self.UPDATE_DEFINITION, update_data)

			if cursor.rowcount == 0:
				cursor.execute(self.INSERT_DEFINITION, data)
			
			self.connection.commit()
		except Error as e:
			print(e)

	def _create_tables(self):
		try:
			cursor = self.connection.cursor()
			cursor.execute(self.TABLE_DEFINITION)
			self.connection.commit()
		except Error as e:
			print(e)

	def dict_factory(self, cursor, row):
		data = {}
		for idx, col in enumerate(cursor.description):
			data[col[0]] = row[idx]
		return data


if __name__ == "__main__":
	Storage().import_csv()