import os
import configparser
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for, redirect, flash, jsonify, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

config = configparser.ConfigParser()

config_paths = [
	os.path.expanduser("~") + "/.s2db/s2db.ini",
	'/etc/s2db/s2db.ini',
	'/etc/s2db.ini',
	'./s2db.ini'
]
for config_path in config_paths:
	if config.read(config_path) != []:
		break
app.config['SQLALCHEMY_DATABASE_URI'] = config['db']['admin']
app.config['UPLOAD_FOLDER'] = config['storage']['path']
app.config['LOG_FILE_PATH'] = config['log']['path']
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

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

@app.route('/ref', methods=['GET'])
def ref():
	sample = request.args.get('h')
	if sample:
		# add sample to ref set
		print("ja lol ey")
		db.session.execute('update bin set ref = true where bin=unhex(:bin)', {'bin': sample})
		db.session.commit()
	cur = db.session.execute('select name, hex(bin) as bin from bin where ref = True order by name asc')
	entries = cur.fetchall()
	return render_template('ref.html', entries=entries)


@app.route('/samples', methods=['GET'])
def samples():
	sample = request.args.get('h')
	if sample:
		print("noooo")
		# remove sample from ref set
		db.session.execute('update bin set ref = false where bin=unhex(:bin)', {'bin': sample})
		db.session.commit()
	cur = db.session.execute('select name, hex(bin) as bin from bin where ref = False order by name asc')
	entries = cur.fetchall()
	return render_template('samples.html', entries=entries)


@app.route('/seqs', methods=['GET'])
def seqs():
	sample = request.args.get('h')
	cur = db.session.execute("""
select names, rep from (
	select group_concat(distinct ref.name) as names, ref.seq as seq from (
		select name,seq from bin join bin2seq on bin.bin = bin2seq.bin where bin.ref=true
	) as ref
	join bin2seq as test on ref.seq = test.seq where test.bin=unhex(:bin)
	group by ref.seq
) as res
join seq on res.seq = seq.seq
order by seq.type desc
	""", {'bin': sample})
	entries = cur.fetchall()
	return render_template('seqs.html', sample=sample, entries=entries)


@app.route('/seq', methods=['GET'])
def seq():
	h = request.args.get('h')
	cur = db.session.execute('select hex(seq) as seq,type,rep from seq where seq=unhex(:seq)', {'seq': h})
	entries = cur.fetchall()
	return render_template('seq.html', seq=h, entries=entries)


@app.route('/sample', methods=['GET'])
def sample():
	sample = request.args.get('h')
	cur = db.session.execute("select count(*) as count, names from (select group_concat(distinct ref.name) as names, hex(ref.seq) from (select name,seq from bin join bin2seq on bin.bin = bin2seq.bin where bin.ref=true) as ref join bin2seq as test on ref.seq = test.seq where test.bin=unhex(:bin) group by ref.seq) as res group by res.names order by count desc", {'bin': sample})
	entries = cur.fetchall()
	return render_template('sample.html', sample=sample, entries=entries)


@app.route('/log')
def log():
	with open(app.config['LOG_FILE_PATH'],'r') as f:
		log = f.read()
	return render_template('log.html', log=log)

if __name__ == "__main__":
	app.run(debug=True)

