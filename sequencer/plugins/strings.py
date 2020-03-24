import sys
import os
import hashlib
import json
import base64

from sequencer import Sequencer

class Sequencer(Sequencer):
	VERSION = 1
	NAME = 'strings'

	payload_sha256 = None
	payload_mime = None
	payload_path = None

	def __init__(self, payload_sha256, payload_mime, payload_path):
		self.payload_sha256 = payload_sha256
		self.payload_mime = payload_mime
		self.payload_path = payload_path
		
	#	bin_data = open(bin_path,'rb').read()
	#	bin_sha256 = hashlib.sha256(bin_data).digest()
		
		# TODO: call strings

		return


