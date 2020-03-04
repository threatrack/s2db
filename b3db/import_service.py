import configparser
import os
import time

if __name__ == '__main__':
	self_path = os.path.abspath(os.path.dirname(__file__))
	config = configparser.ConfigParser()
	config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),"b3db.ini")
	config.read(config_path)
	storage_path = config['storage']['path']

	while True:
		print('Checking upload queue folder...')
		for fn in os.listdir(storage_path):
			print('Processing ' + fn + '...')
			file_path = storage_path + '/' + fn
			os.system('python3 '+self_path+'/extract_features.py '+file_path)
			os.remove(file_path)
		time.sleep(3)

