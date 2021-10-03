import os
import sys
from flask import Flask, render_template, url_for, redirect, flash, jsonify, request, g, send_from_directory
from werkzeug.utils import secure_filename
import hashlib
import re
import time

_S2DB_ROOT = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
sys.path.append(_S2DB_ROOT)

from common.config import config
from common.log import get_logger
from db.engine import *


REGEX_SHA265 = re.compile('^[A-Fa-f0-9]{64}$')


logger = get_logger(__name__)

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = config['storage'].get('path', raw=True)
app.config['LOG_FILE_PATH'] = config['log'].get('path', raw=True)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024


@app.route('/')
def index():
	return render_template('app.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/api/v0/software', methods=['POST'], strict_slashes=False)
@app.route('/api/v0/software/<string:parent>', methods=['POST'], strict_slashes=False)
def add_file(parent=None):
	cls = request.args.get('class')
	family = request.args.get('family')
	name = request.args.get('name')
	if (parent and not REGEX_SHA265.match(parent)) or \
	   (request.method != 'POST') or \
	   (cls and len(cls)>64) or \
	   (family and len(family)>64) or \
	   (name and len(name)>64):
		return '',400
	file = request.files.get('file')
	if file:
		filename = secure_filename(file.filename)
		filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		file.save(filepath)
		file.seek(0)
		hash = hashlib.sha256(file.read()).hexdigest()
		db_sequencer_task_add(hash,filepath,parent,cls,family,name)
		return f"{{\"software\":\"{hash}\"}}",200
	elif parent and (cls or family or name):
		db_set_classfamilyname(parent, cls, family, name)
		return '',200
	return '',400


@app.route('/api/v0/software/<string:hash>', methods=['GET'], strict_slashes=False)
def get_software(hash):
	software = db_get_software(hash)
	if software:
		return jsonify(software),200
	return "",404


@app.route('/api/v0/softwaretree/<string:hash>', methods=['GET'], strict_slashes=False)
def get_softwaretree(hash):
	return jsonify(db_get_softwaretree(hash)),200


@app.route('/api/v0/softwares', methods=['GET'], strict_slashes=False)
@app.route('/api/v0/softwares/<int:limit>', methods=['GET'], strict_slashes=False)
@app.route('/api/v0/softwares/<int:limit>/<int:offset>', methods=['GET'], strict_slashes=False)
def get_softwares(limit=10000,offset=0):
	return jsonify(db_get_softwares(limit,offset)),200


@app.route('/api/v0/softwaressequences/<hash>', methods=['GET'], strict_slashes=False)
@app.route('/api/v0/softwaressequences/<hash>/<int:limit>', methods=['GET'], strict_slashes=False)
@app.route('/api/v0/softwaressequences/<hash>/<int:limit>/<int:offset>', methods=['GET'], strict_slashes=False)
def get_softwaressequences(hash,limit=10000,offset=0):
	return jsonify(db_get_softwaressequences(hash)),200

@app.route('/api/v0/softwaressequencesgrouped/<hash>', methods=['GET'], strict_slashes=False)
@app.route('/api/v0/softwaressequencesgrouped/<hash>/<int:limit>', methods=['GET'], strict_slashes=False)
@app.route('/api/v0/softwaressequencesgrouped/<hash>/<int:limit>/<int:offset>', methods=['GET'], strict_slashes=False)
def get_softwaressequencesgrouped(hash,limit=10000,offset=0):
	return jsonify(db_get_softwaressequencesgrouped(hash)),200

if __name__ == "__main__":
	app.run(host=config['web'].get('host','0.0.0.0', raw=True), port=config['web'].getint('port', 5000, raw=True), debug=True)



