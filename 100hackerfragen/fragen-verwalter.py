from flask import Flask, render_template, request, make_response
from manage import get_frage, set_ready, unset_ready, add_antwort, add_frage, get_ready_state_by_id,\
    add_downvote, list_fragen, get_frage_by_id, get_finished_frage, normalized_antworten, update_antwort
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
def list():
    out = []
    for frage in list_fragen():
        out.append([frage[0], frage[1]])
    return render_template(
        "fragenliste.html",
        fragen=out
    )


@app.route('/edit')
def index():
    data = to_dict(request.args)
    if 'new_antwort' in data:
        ids = request.values.getlist('ids')
        for a_id in ids:
            for b_id in eval(a_id):
                update_antwort(b_id, data['new_antwort'])

    if 'frage_id' in request.args:
        frage = get_frage_by_id(data['frage_id'])
    elif 'processed_frage_id' in data:
        frage = get_frage_by_id(data['processed_frage_id'])    
    else:
        frage = get_finished_frage()

    if frage is None:
        return "Something went wrong or no finished fragen."

    frage_id = frage[0]
    frage = frage[1]

    if 'finished' in data:
        set_ready(frage_id)
        fertig = "checked"
    else:
        unset_ready(frage_id)
        fertig = ""

    ants = normalized_antworten(frage_id)

    return render_template(
        'admin.html', 
        frage=frage,
        fertig=fertig,
        frage_id=frage_id,
        antworten=ants,
        approot=APPROOT)
