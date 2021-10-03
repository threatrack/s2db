import sys
import magic
import hashlib
import os
import configparser

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import sqlalchemy

import requests
import json
import pyzipper

def get_config():
	config = configparser.ConfigParser()
	config_paths = [
		os.path.expanduser("~") + "/.s2db/s2db.ini",
		'/etc/s2db/s2db.ini',
		'/etc/s2db.ini',
		'/opt/s2db.ini',
		'./s2db.ini'
	]
	for config_path in config_paths:
		if config.read(config_path) != []:
			break
	return config

def foo():
	db_base = automap_base()
	db_engine = sqlalchemy.create_engine(config['db']['insert'])
	db_base.prepare(db_engine, reflect=True)
	db_bin = db_base.classes.bin
	db_bin2seq = db_base.classes.bin2seq
	db_seq = db_base.classes.seq
	
	db_session = Session(db_engine)
	
	db_session.merge(db_bin(bin=self.payload_sha256,name=self.payload_name,ref=self.ref))
	
	for s in self.seq:
		db_session.merge(db_bin2seq(bin=self.payload_sha256,seq=s['seq']))
		db_session.merge(db_seq(seq=s['seq'],type=s['type'],rep=s['rep']))
		db_session.commit()

if __name__ == '__main__':
	config = get_config()
	capev2_url = config['capev2']['url']
	sample_path = 
	db_base = automap_base()
	db_engine = sqlalchemy.create_engine(config['db']['insert'])
	db_base.prepare(db_engine, reflect=True)
	db_bin = db_base.classes.bin
	db_bin2seq = db_base.classes.bin2seq
	db_seq = db_base.classes.seq
	db_seq = db_base.classes.jobs
	
	db_session = Session(db_engine)
	cur = db_session.e
	for i in [1]:
		r = requests.get(capev2_url + '/api/cuckoo/status/')
		if r.status_code != 200:
			print "CAPE error"
			break
		j = json.loads(r.content)
		j['error'] != False:
			print "CAPE error"
			break
		r = requests.get(capev2_url + '/api/files/view/sha256/b51044c0907e71393cb3eed65be6f7f84ff0a75b26c5f7f64d57d58d355c514e/')
		j = json.loads(r.content)
		j['error'] != False:
			print "CAPE error"
			break
		task_id = j['data']['id']
		r = requests.get(capev2_url + '/api/tasks/get/procdumpfiles/'+str(task_id)+'/')
		data = r.content
		if data[:2] != b'PK':
			print "CAPE error"
			break
		# FIXME: avoid touching disk
		path = hashlib.sha256(data).hexdigest()	
		open(path,"wb").write(data)
		zf = pyzipper.AESZipFile(path)	
		for f in zf.namelist():
			zf.extract(f,path=,pwd=b'infected')
		
		db_session.merge(db_bin(bin=self.payload_sha256,name=self.payload_name,ref=self.ref))
		
		for s in self.seq:
			db_session.merge(db_bin2seq(bin=self.payload_sha256,seq=s['seq']))
			db_session.merge(db_seq(seq=s['seq'],type=s['type'],rep=s['rep']))
			db_session.commit()

