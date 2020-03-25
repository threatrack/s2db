import configparser
import os
import sys
import time
import datetime

config = configparser.ConfigParser()

config_paths = [
	os.path.expanduser("~") + "/.s2db/s2db.ini",
	'/etc/s2db/s2db.ini',
	'/etc/s2db.ini',
	'./s2db.ini'
]
for config_path in config_paths:
	if config.read(config_path) != []:
		break

storage_path = config['storage']['path']

if __name__ == '__main__':
	self_path = os.path.abspath(os.path.dirname(__file__))

	print(__file__+' started ...', flush=True)

	while True:
		for fn in os.listdir(storage_path):
			print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + fn, flush=True)
			file_path = storage_path + '/' + fn
			os.system('python3 '+self_path+'/sequencer.py '+file_path)
			os.remove(file_path)
		time.sleep(3)

