import sys
import os
import hashlib
import json
import base64
import re

import subprocess

class Sequencer():
	VERSION = 1
	NAME = 'strings'
	
	payload_path = None
	payload_sha256 = None
	payload_mime = None
	payload_name = None
	
	def __init__(this, payload_sha256, payload_mime, payload_path):
		this.payload_sha256 = payload_sha256
		this.payload_mime = payload_mime
		this.payload_path = payload_path
		this.payload_name = os.path.basename(payload_path)
	
	def sequence(this):
		# TODO: FIXME: Maybe run with --include-all-whitespace
		p = subprocess.Popen(["strings", "-a", "-es", this.payload_path], stdout=subprocess.PIPE)
		out, err = p.communicate()
		
		valid_string_regex = re.compile(b"^([A-Za-z0-9]{4,}|[A-Za-z0-9:./\\\]{6,}|.{8,})$")
	
		strings = []
		for s in out.split(b'\n'):
			string = s.decode('utf-8')
			if valid_string_regex.match(s):
				strings.append( (hashlib.sha256(s).hexdigest(), s) )
		this.seq = []
		for s in strings:
			this.seq.append({"representation":s.decode('utf-8'), "signature":s.hex(), "type":"string", "sequence":hashlib.sha256(s).hexdigest()})
		return this.seq

