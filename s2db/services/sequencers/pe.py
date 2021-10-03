import r2pipe
import sys
import os
import hashlib
import json
import base64
import re
from capstone import *

class Sequencer():
	VERSION = 1
	NAME = "pe"

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
		bin_path = this.payload_path
		bin_data = open(this.payload_path,'rb').read()
		bin_sha256 = this.payload_sha256

		r2 = r2pipe.open(bin_path, flags=['-2'])
		r2.cmd('aaaa')
		
		info = r2.cmdj('ij')
		
		strings_json = r2.cmdj('izj')
		
		strings = []
		
		valid_string_regex = re.compile("^([A-Za-z0-9]{4,}|[A-Za-z0-9:./\\\]{6,}|.{8,})$")
		
		for s in strings_json:
			# FIXME: we "loose" the encoding in s['type'] here
			# so a utf-8 strings will be treated the same as the same string but in ascii
			#s = base64.b64decode(s['string']).decode('utf-8')
			s = s['string']
			if valid_string_regex.match(s):
				strings.append( (hashlib.sha256(s.encode('utf-8')).hexdigest(), s) )
		
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
		
		if info['bin']['arch'] == 'x86' and info['bin']['bits'] == 64 and info['bin']['class'] == 'PE32+':
			md = Cs(CS_ARCH_X86, CS_MODE_64)
		elif info['bin']['arch'] == 'x86' and info['bin']['bits'] == 32 and info['bin']['class'] == 'PE32':
			md = Cs(CS_ARCH_X86, CS_MODE_32)
		else:
			raise Exception("Unknown PE file")
		md.detail = True
		md.syntax = CS_OPT_SYNTAX_INTEL
		
		def get_masked(inst):
			code = inst.bytes
			hex = list(inst.bytes.hex())
			for i in range(inst.imm_offset, inst.imm_offset + inst.imm_size):
				code[i] = 0
				hex[i*2+0] = "?"
				hex[i*2+1] = "?"
			for i in range(inst.disp_offset, inst.disp_offset + inst.disp_size):
				code[i] = 0
				hex[i*2+0] = "?"
				hex[i*2+1] = "?"
			return code, "".join(hex)
		
		masked_bb = []
		
		for b in bb:
			masked_b = b''
			disasm_b = ''
			sig_b = ''
			for i in md.disasm(b, 0):
				force_mask = False
				for g in i.groups:
					if i.group_name(g) in ['call', 'jump']:
						force_mask = True
				if force_mask or i.imm_size > 1 or i.disp_size > 1:
					code,hex = get_masked(i)
					masked_b += code
					sig_b += hex
				else:
					masked_b += i.bytes
					sig_b += i.bytes.hex()
				for m in md.disasm(masked_b,0):
					disasm_b += m.mnemonic + '\t' + m.op_str + '\n'
			masked_bb.append((hashlib.sha256(masked_b).hexdigest(),disasm_b,sig_b))
		
		# make lists unique
		masked_bb = list(set(masked_bb))
		strings = list(set(strings))

		this.seq = []
		for s in strings:
			this.seq.append({"type": "string", "sequence":s[0], "representation":s[1], "signature":s[1].encode("utf-8").hex()})
		for b in masked_bb:
			this.seq.append({"type":"basicblock", "sequence":b[0], "representation":b[1], "signature":b[2]})

		return this.seq


