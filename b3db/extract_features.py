#!/usr/bin/python3.6
import r2pipe
import sys
import os
import hashlib
import json
import base64
from capstone import *

import configparser

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import sqlalchemy

bin_path = sys.argv[1]

bin_data = open(bin_path,'rb').read()
bin_sha256 = hashlib.sha256(bin_data).digest()

r2 = r2pipe.open(bin_path, flags=['-2'])
r2.cmd('aaaa')

strings_json = r2.cmdj('izj')

strings = []

for s in strings_json:
	# FIXME: we "loose" the encoding in s['type'] here
	# so a utf-8 strings will be treated the same as the same string but in ascii
	#s = base64.b64decode(s['string']).decode('utf-8')
	s = s['string'].encode('utf-8')
	strings.append( [hashlib.sha256(s).digest(), s] )

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

#####
# put into db
#####

config = configparser.ConfigParser()
config_path=os.path.join(os.path.abspath(os.path.dirname(__file__)),"b3db.ini")
config.read(config_path)

db_base = automap_base()
db_engine = sqlalchemy.create_engine(config['db']['path'])
db_base.prepare(db_engine, reflect=True)
db_bin = db_base.classes.bin
db_bb = db_base.classes.bb

db_session = Session(db_engine)

db_session.merge(db_bin(bin=bin_sha256,name=bin_path))

#for s in strings:
	#print(bin_path +'\t'+ s[0] +'\t'+ s[1])
#	session.merge()

for b in masked_bb:
	#print(bin_path +'\t'+ b[0].hex() +'\t'+ b[1].replace('\n','; '))
	db_session.merge(db_bb(bin=bin_sha256,bb=b[0]))

db_session.commit()


