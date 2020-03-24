import sys
import magic
import hashlib
import os
import configparser

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import sqlalchemy

class Sequencer:
	def factory(payload_path, ref=False):
		from plugins import pe
		from plugins import strings
		plugins = {
			'application/x-dosexec' : pe.Sequencer
		}
		payload_mime = magic.from_file(payload_path, mime=True)
		with open(payload_path, 'rb') as f:
			payload_data = f.read()
		payload_sha256 = hashlib.sha256(payload_data).digest()
		const = plugins.get(payload_mime, strings.Sequencer)
		return const(payload_sha256, payload_mime, payload_path, ref=False)

	def commit(self):
		config = configparser.ConfigParser()
		config_path=os.path.expanduser("~") + "/.s2db/s2db.ini"
		config.read(config_path)
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
	s = Sequencer.factory(sys.argv[1])
	print(s.NAME)
	print(s.payload_name)
	print("Sequencing...")
	seq = s.sequence()
	print("Committing...")
	s.commit()
#	for s in seq:
#		print(s['type']+':'+s['rep'])

