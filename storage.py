import sqlite3
import os
from sqlite3 import Error

class Storage:

	IS_DEBUG    = 'raspberrypi' not in os.uname()
	DB_NAME 	= "covid19.sqlite"
	LOCAL_PATH	= '.'
	RPI_PATH	= '/home/pi/pi-display/'

	TABLE_DEFINITION = '''
CREATE TABLE IF NOT EXISTS entries (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	area TEXT,
	total_cases INTEGER,
	new_cases INTEGER,
	total_deaths INTEGER,
	new_deaths INTEGER,
	total_recovered INTEGER,
	critical_cases INTEGER,
	timestamp INTEGER
);
'''
	INSERT_DEFINITION = '''
INSERT INTO 
	entries 
VALUES
	(NULL, :area, :total_cases, :new_cases, :total_deaths, :total_recovered, :total_recovered, :critical_cases, :timestamp)
'''

	connection 	= None
	
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

	def add(self, data):
		try:
			cursor = self.connection.cursor()
			cursor.execute(self.INSERT_DEFINITION, data)
			print(cursor.rowcount)
		except Error as e:
			print(e)

	def _create_tables(self):
		try:
			cursor = self.connection.cursor()
			cursor.execute(self.TABLE_DEFINITION)
		except Error as e:
			print(e)