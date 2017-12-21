from flask import Flask, render_template, request
from manage import get_frage, add_antwort, add_frage

app = Flask("100hackerfragen-on-the-web")


def to_dict(args):
    outdict = {}
    for key, val in args.items():
        outdict[key] = val
    return outdict


@app.route('/')
def index():
	data = to_dict(request.args)
	if 'answer' in data.keys() and 'frage_id' in data.keys():
		add_antwort(data['frage_id'], data['answer'])
	return render_template('index.html', frage=get_frage())


@app.route('/add')
def add():
	data = to_dict(request.args)
	submitted = False
	if 'question' in data.keys():
		add_frage(data['question'])
		submitted = True
	return render_template('addfrage.html', submitted=submitted)
