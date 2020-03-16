import os
import configparser
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for, redirect, flash, jsonify, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

config = configparser.ConfigParser()
config_path=os.path.join(os.path.abspath(os.path.dirname(__file__)),"../b3db.ini")
config.read(config_path)
app.config['SQLALCHEMY_DATABASE_URI'] = config['db']['path']
app.config['UPLOAD_FOLDER'] = config['storage']['path']
app.config['LOG_FILE_PATH'] = config['log']['path']

db = SQLAlchemy(app)


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit an empty part without filename
		if file.filename == '':
			return redirect(request.url)
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		return redirect(url_for('upload', filename=filename))
	return render_template('upload.html')


@app.route('/ref')
def ref():
	cur = db.session.execute('select name, hex(bin) as bin from bin where ref = True order by name asc')
	entries = cur.fetchall()
	return render_template('ref.html', entries=entries)

@app.route('/samples')
def samples():
	cur = db.session.execute('select name, hex(bin) as bin from bin where ref = False order by name asc')
	entries = cur.fetchall()
	return render_template('samples.html', entries=entries)

@app.route('/blocks', methods=['GET'])
def blocks():
	sample = request.args.get('h')
	cur = db.session.execute('select hex(block) as block from b2b where bin=unhex(:bin)', {'bin': sample})
	entries = cur.fetchall()
	return render_template('blocks.html', sample=sample, entries=entries)

@app.route('/block', methods=['GET'])
def block():
	h = request.args.get('h')
	cur = db.session.execute('select hex(block) as block,type,rep from block where block=unhex(:block)', {'block': h})
	entries = cur.fetchall()
	return render_template('block.html', block=h, entries=entries)

@app.route('/sample', methods=['GET'])
def sample():
	sample = request.args.get('h')
	cur = db.session.execute("select count(*) as count, names from (select group_concat(distinct ref.name) as names, hex(ref.block) from (select name,block from bin join b2b on bin.bin = b2b.bin where bin.ref=true) as ref join b2b as test on ref.block = test.block where test.bin=unhex(:bin) group by ref.block) as res group by res.names order by count desc", {'bin': sample}
	)
	entries = cur.fetchall()
	return render_template('sample.html', sample=sample, entries=entries)

@app.route('/log')
def log():
	with open(app.config['LOG_FILE_PATH'],'r') as f:
		log = f.read()
	return render_template('log.html', log=log)

if __name__ == "__main__":
	app.run(debug=True)

