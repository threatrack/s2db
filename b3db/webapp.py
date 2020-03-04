import os
import configparser
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for, redirect, flash, jsonify, request
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/home/user/b3db/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

config = configparser.ConfigParser()
config_path=os.path.join(os.path.abspath(os.path.dirname(__file__)),"b3db.ini")
config.read(config_path)
app.config['SQLALCHEMY_DATABASE_URI'] = config['db']['path']

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


@app.route('/samples')
def samples():
	cur = db.session.execute('select name, hex(bin) as bin from bin order by name asc')
	entries = cur.fetchall()
	return render_template('samples.html', entries=entries)


@app.route('/sample', methods=['GET'])
def sample():
	sample = request.args.get('h')
	cur = db.session.execute("select count(*) as count, names from (select group_concat(distinct ref.name) as names, hex(ref.bb) from (select name,bb from bin join bb on bin.bin = bb.bin where bin.ref) as ref join bb as test on ref.bb = test.bb where test.bin=unhex(:bin) group by ref.bb) as res group by res.names order by count desc",
    {'bin': sample}
	)
	entries = cur.fetchall()
	return render_template('sample.html', sample=sample, entries=entries)

if __name__ == "__main__":
	app.run(debug=True)

