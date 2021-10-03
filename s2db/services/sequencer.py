import sys
import magic
import hashlib
import os
import sqlalchemy
import time
import argparse

_S2DB_ROOT = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))
sys.path.append(_S2DB_ROOT)

from common.config import config
from common.log import get_logger
from db.engine import *

logger = get_logger(__name__)

def sequencer_factory(payload_path):
	from services.sequencers import pe
	from services.sequencers import strings
	plugins = {
		'application/x-dosexec' : pe.Sequencer
	}
	payload_mime = magic.from_file(payload_path, mime=True)
	with open(payload_path, 'rb') as f:
		payload_data = f.read()
	payload_sha256 = hashlib.sha256(payload_data).hexdigest()
	sequencer = plugins.get(payload_mime, strings.Sequencer)
	return sequencer(payload_sha256, payload_mime, payload_path)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Run S2DB sequencer.")
	parser.add_argument("-w","--worker", type=int, help="unique sequencer worker ID", required=True)
	args = parser.parse_args()
	worker = args.worker
	# wait so DB can start up; TODO: make a proper wait
	time.sleep(1)
	logger.info("started")
	while True:
		task = db_sequencer_task_get_and_set_start(worker)
		if task is None or task.get("path") is None:
			time.sleep(5)
			logger.info("no tasks")
		else:
			path = task["path"]
			parent = task.get("parent")
			logger.info("processing %s as child of %s" % (path, parent))
			sequencer = sequencer_factory(path)
			if not db_software_exists(sequencer.payload_sha256):
				sequences = sequencer.sequence()
				db_sequences_add(sequencer.payload_sha256, sequences)
				db_software_add(
					sequencer.payload_sha256,
					sequencer.payload_mime,
					parent,
					task.get("class"),
					task.get("family"),
					task.get("name")
				)
			else:
				logger.info("software already exists in database")
			db_sequencer_task_remove(path)

