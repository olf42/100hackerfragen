import sqlite3
import random


def setup_db():
    db = sqlite3.connect('100hackerfragen.db')
    c = db.cursor()
    c.execute('''
        CREATE TABLE fragen (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            frage TEXT,
            downvotes INTEGER,
            prio INTEGER default 0,
            status TEXT default "")''')
    c.execute('''
        CREATE TABLE antworten (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            antwort TEXT, 
            frage_id INTEGER, 
        FOREIGN KEY (frage_id) REFERENCES fragen(id))''')
    db.commit()
    db.close()


def db(func):
    def func_wrapper(*args, **kw):
        db = sqlite3.connect('100hackerfragen.db')
        c = db.cursor()
        res = func(c, *args, **kw)
        db.commit()
        db.close()
        return res
    return func_wrapper


@db
def add_frage(c, frage):
    c.execute('INSERT INTO fragen (frage, downvotes) VALUES (?, 0)', (frage,))

@db
def add_downvote(c, frage_id):
    c.execute('UPDATE fragen SET downvotes=(SELECT downvotes+1 FROM fragen WHERE id=(?)) WHERE id=(?)', (frage_id, frage_id))

@db
def add_antwort(c, frage_id, antwort):
    c.execute('SELECT downvotes FROM fragen WHERE id=(?)', (frage_id,))
    res = c.fetchone()
    if res[0] > 0:
        c.execute('UPDATE fragen SET downvotes=(SELECT downvotes-1 FROM fragen WHERE id=(?)) WHERE id=(?)', (frage_id, frage_id))
    c.execute('INSERT INTO antworten (frage_id, antwort) VALUES (?, ?)',
                (frage_id, antwort))

@db
def get_frage(c, already_asked_ids):
    """Returns frage with least answers, return None if there are no fragen with < 100 answers"""
    q = '''SELECT * from (
                SELECT 
                    fragen.id,
                    fragen.frage, 
                    fragen.downvotes as downvotes,
                    fragen.prio as prio,
                    count(antworten.id) AS num_antworten 
                FROM fragen
                LEFT JOIN antworten ON antworten.frage_id=fragen.id 
                GROUP BY fragen.id)
            WHERE num_antworten < 100 
                AND downvotes < 3
                AND id NOT IN (%s)
            ORDER BY prio DESC, num_antworten DESC''' % (str(list(already_asked_ids)).replace('[','').replace(']',''))
    c.execute(q)
    res = c.fetchone()
    if not res:
        return
    id, fr, dv, num = res
    return dict(id=id, frage=fr, num=num)


@db
def get_finished_frage(c):
    """returns next finished frage"""
    q = '''SELECT * from (
                SELECT 
                    fragen.id,
                    fragen.frage, 
                    fragen.downvotes as downvotes,
                    fragen.status as status,
                    count(antworten.id) AS num_antworten 
                FROM fragen
                LEFT JOIN antworten ON antworten.frage_id=fragen.id 
                GROUP BY fragen.id)
            WHERE num_antworten >= 100 
                AND downvotes < 3
                AND status=""'''
    c.execute(q)
    res = c.fetchone()
    if res:
        return res
    return

@db
def get_frage_by_id(c, id):
    c.execute("SELECT id, frage FROM fragen WHERE id=(?)", (id,))
    res = c.fetchone()
    if res:
        return res
    return

@db
def get_antworten(c, frage_id):
    q = '''SELECT id, antwort from antworten WHERE frage_id=(?)'''
    c.execute(q, (frage_id,))
    return c.fetchall()


@db
def update_antwort(c, id, new_antwort):
    q = '''UPDATE antworten SET antwort=(?) WHERE id=(?)'''
    c.execute(q, (new_antwort, id))

@db
def set_ready(c, id):
    q = '''UPDATE fragen SET status="ready" WHERE id=(?)'''
    c.execute(q, (id,))

@db
def get_stats(c):
    q = '''SELECT * from (
            SELECT 
                fragen.id,
                fragen.frage, 
                fragen.downvotes as downvotes,
                count(antworten.id) AS num_antworten 
            FROM fragen
            LEFT JOIN antworten ON antworten.frage_id=fragen.id 
            GROUP BY fragen.id)
        ORDER BY num_antworten DESC'''
    c.execute(q)
    return c.fetchall()

@db
def len_fragen(c):
    c.execute("SELECT count(*) from fragen")
    return c.fetchone()[0]

@db
def len_antworten(c):
    return c.execute("SELECT count(*) from antworten").fetchone()[0]

print("Hello. We currently have {} questions and {} answers.".format(len_fragen(), len_antworten()))
