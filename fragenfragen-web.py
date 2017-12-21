from flask import Flask, render_template, request
from manage import get_frage, add_antwort, add_frage

app = Flask("100hackerfragen-on-the-web")

class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

app.wsgi_app = ReverseProxied(app.wsgi_app)



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
