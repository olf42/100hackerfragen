from flask import Flask, render_template, request, make_response
from manage import get_frage, add_antwort, add_frage
from config import APPROOT

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
	hfq = request.cookies.get('1hfq', '')
	data = to_dict(request.args)
	answered_id = None
	if 'answer' in data.keys() and 'frage_id' in data.keys():
		answered_id = data['frage_id']
		add_antwort(answered_id, data['answer'])
	tries = 0
	while True:
		tries += 1
		frage = get_frage()
		if '"{}"'.format(frage['id']) not in hfq and str(frage['id']) != answered_id:
			no_more_questions = False
			break
		if tries == 100:
			no_more_questions = True
			break
	resp = make_response(render_template(
		'index.html', 
		frage=frage, 
		no_more_questions=no_more_questions, 
		approot=APPROOT))
	if answered_id:
		hfq = '{},"{}"'.format(hfq, answered_id)
		resp.set_cookie('1hfq', hfq)
	return resp


@app.route('/add')
def add():
	data = to_dict(request.args)
	submitted = False
	if 'question' in data.keys():
		add_frage(data['question'])
		submitted = True
	return render_template('addfrage.html', submitted=submitted, approot=APPROOT)
