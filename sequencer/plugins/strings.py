import sys
import os
import hashlib
import json
import base64

import subprocess

from sequencer import Sequencer

class Sequencer(Sequencer):
	VERSION = 1
	NAME = 'strings'

	payload_path = None
	payload_sha256 = None
	payload_mime = None
	payload_name = None
	ref = False

	seq = []

	def __init__(self, payload_sha256, payload_mime, payload_path, ref=False):
		self.payload_sha256 = payload_sha256
		self.payload_mime = payload_mime
		self.payload_path = payload_path
		self.payload_name = os.path.basename(payload_path)
		self.ref = ref
		return

	def sequence(self):
		# TODO: FIXME: Maybe run with --include-all-whitespace
		p = subprocess.Popen(["strings", "-a", "-es", self.payload_path], stdout=subprocess.PIPE)
		out, err = p.communicate()
		for s in out.split(b'\n'):
			self.seq.append({'rep':s.decode('utf-8'), 'type':'ascii', 'seq':hashlib.sha256(s).digest()})
		return self.seq

