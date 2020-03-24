import r2pipe
import sys
import os
import hashlib
import json
import base64
from capstone import *

from sequencer import Sequencer

class Sequencer(Sequencer):
	VERSION = 1
	NAME = "pe_x86"

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
		bin_path = self.payload_path
		bin_data = open(self.payload_path,'rb').read()
		bin_sha256 = self.payload_sha256

		r2 = r2pipe.open(bin_path, flags=['-2'])
		r2.cmd('aaaa')
		
		strings_json = r2.cmdj('izj')
		
		strings = []
		
		for s in strings_json:
			# FIXME: we "loose" the encoding in s['type'] here
			# so a utf-8 strings will be treated the same as the same string but in ascii
			#s = base64.b64decode(s['string']).decode('utf-8')
			s = s['string']
			strings.append( [hashlib.sha256(s.encode('utf-8')).digest(), s] )
		
		results = r2.cmd('pdbj @@ *').split('\n')
		results.remove('')
		
		temp = set()
		
		for r in results:
			temp.add(r)
		temp = list(temp)
		
		bb = []
		
		for t in temp:
			tbb = json.loads(t)
			offset = tbb[0]['offset']
			code = b''
			for b in tbb:
				code += bytes.fromhex(b['bytes'])
			bb.append(code)
		
		md = Cs(CS_ARCH_X86, CS_MODE_32)
		md.detail = True
		md.syntax = CS_OPT_SYNTAX_INTEL
		
		def get_masked(inst):
			code = inst.bytes
			for i in range(inst.imm_offset, inst.imm_offset + inst.imm_size):
				code[i] = 0
			for i in range(inst.disp_offset, inst.disp_offset + inst.disp_size):
				code[i] = 0
			return code
		
		masked_bb = []
		
		for b in bb:
			masked_b = b''
			disasm_b = ''
			for i in md.disasm(b, 0):
				#print("%s\t%s\t%s\t%d\t%d" %(i.mnemonic, i.op_str, i.insn_name(), i.imm_size, i.disp_size))
				disasm_b += i.mnemonic + '\t' + i.op_str + '\n'
				force_mask = False
				for g in i.groups:
					if i.group_name(g) in ['call', 'jump']:
						force_mask = True
				if force_mask or i.imm_size > 1 or i.disp_size > 1:
					masked_b += get_masked(i)
				else:
					masked_b += i.bytes
		
			masked_bb.append((hashlib.sha256(masked_b).digest(),disasm_b))
		
		# make list unique
		masked_bb = list(set(masked_bb))

		self.seq = []
		for s in strings:
			self.seq.append({'type': 'string', 'seq':s[0], 'rep':s[1]})
		for b in masked_bb:
			self.seq.append({'type':'basicblock', 'seq':b[0], 'rep':b[1]})

		return self.seq


