from flask import Flask, render_template, request, make_response
from manage import get_frage, get_ready_fragen, set_ready, add_antwort, add_frage, add_downvote, get_frage_by_id, get_finished_frage, normalized_antworten, update_antwort
from config import APPROOT

app = Flask("100hackerfragen-game-web")

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
    fragen = get_ready_fragen()
    return render_template(
        'fragenliste.html', 
        fragen=fragen,
        approot=APPROOT)


@app.route('/reveal')
def reveal():
    data = to_dict(request.args)
    txt = data['txt']
    anzahl = data['anzahl']
    if len(anzahl) == 1:
        anzahl = ' '+anzahl
    platz = data['platz']
    with open('message', 'w') as f:
        f.write('{}{}{}'.format(platz, txt, anzahl))
    return frage()


@app.route('/frage')
def frage():
    data = to_dict(request.args)

    frage = get_frage_by_id(data['frage_id'])

    frage_id = frage[0]
    frage = frage[1]

    ants = normalized_antworten(frage_id)

    return render_template(
        'frage.html', 
        frage=frage,
        frage_id=frage_id,
        antworten=ants,
        approot=APPROOT)