from flask import Flask, render_template, request, make_response
from manage import get_frage, set_ready, add_antwort, add_frage, add_downvote, get_frage_by_id, get_finished_frage, get_antworten, update_antwort
from config import APPROOT

app = Flask("100hackerfragen-verwalter")

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


REPLACE = ['-',' ','!', '?',':)',';-)',';)']

def normalize(antwort):
    antwort = antwort.lower().strip()
    for sc in REPLACE:
        antwort = antwort.replace(sc, '')
    return antwort


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
    return index()


@app.route('/')
def index():
    data = to_dict(request.args)
    if 'new_antwort' in data:
        ids = request.values.getlist('ids')
        for a_id in ids:
            for b_id in eval(a_id):
                update_antwort(b_id, data['new_antwort'])

    if 'finished' in data:
        set_ready(data['processed_frage_id'])


    if 'frage_id' in request.args:
        frage = get_frage_by_id(data['frage_id'])
    else:
        frage = get_finished_frage()

    if frage is None:
        return "Something went wrong or no finished fragen."

    frage_id = frage[0]
    frage = frage[1]

    antworten = get_antworten(frage_id)
  

    processed_antworten = dict()

    for id, antwort in antworten:
        norm_ant = normalize(antwort)
        if norm_ant not in processed_antworten:
            processed_antworten[norm_ant] = dict(antwort=antwort, count=1, ids=[id])
        else:
            processed_antworten[norm_ant]['count'] += 1
            processed_antworten[norm_ant]['ids'].append(id)

    res = []
    for pa in processed_antworten.items():
        res.append((pa[1]['count'], pa[1]))

    ants = []
    pi = 0
    for r in reversed(sorted(res, key=lambda x: x[0])):
        pi += 1
        a = r[1]
        a['platz'] = pi
        ants.append(a)

    return render_template(
        'admin.html', 
        frage=frage,
        frage_id=frage_id,
        antworten=ants,
        approot=APPROOT)