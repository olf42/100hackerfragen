from flask_session import Session
from flask import Flask, session, render_template, request, make_response
from dbhandler import get_database
from config import APPROOT, USER_SUBMITTED_QUESTIONS, SALUTATION


SESSION_TYPE = 'filesystem'

db = get_database()

app = Flask(__name__)
app.config.from_object(__name__)
Session(app)


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
    hfq = session.get('1hfq', '')
    already_asked_ids = [int(i.replace('"', '')) for i in hfq.split(',') if i]
    data = to_dict(request.args)
    answered_id = None
    if 'answer' in data.keys() and 'frage_id' in data.keys():
        answered_id = data['frage_id']
        if not(data['answer'].strip() == '' or 'nope' in data.keys() or 'shit' in data.keys()):
            db.add_antwort(answered_id, data['answer'])
            print('{} - {}'.format(db.get_frage_by_id(answered_id), data['answer']))
        if 'shit' in data.keys():
            db.add_downvote(answered_id)
        already_asked_ids.append(answered_id)
    frage = db.get_frage(already_asked_ids)
    no_more_questions = False
    if frage is None:
        no_more_questions = True
    resp = make_response(render_template(
        'index.html',
        frage=frage,
        no_more_questions=no_more_questions,
        approot=APPROOT,
        usq=USER_SUBMITTED_QUESTIONS,
        salutation=SALUTATION))
    if answered_id:
        hfq = '{},"{}"'.format(hfq, answered_id)
        session['1hfq'] = hfq
    return resp


def add():
    data = to_dict(request.args)
    submitted = False
    if 'question' in data.keys():
        db.add_frage(data['question'])
        submitted = True
    return render_template(
        'addfrage.html',
        submitted=submitted,
        approot=APPROOT,
    )

if USER_SUBMITTED_QUESTIONS:
    app.add_url_rule('/add', 'add', add)

