import configparser
import os
import sys
import time
import datetime

if __name__ == '__main__':
	self_path = os.path.abspath(os.path.dirname(__file__))
	config = configparser.ConfigParser()
	config_path=os.path.expanduser("~") + "/.s2db/s2db.ini"
	config.read(config_path)
	storage_path = config['storage']['path']

	print(__file__+' started ...', flush=True)

	while True:
		for fn in os.listdir(storage_path):
			print(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + fn, flush=True)
			file_path = storage_path + '/' + fn
			os.system('python3 '+self_path+'/sequencer.py '+file_path)
			os.remove(file_path)
		time.sleep(3)

