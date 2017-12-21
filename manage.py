import sqlite3
import random


def setup_db():
    db = sqlite3.connect('100hackerfragen.db')
    c = db.cursor()
    c.execute('''
        CREATE TABLE fragen (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            frage TEXT,
            downvotes INTEGER)''')
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
def get_frage(c):
    """Returns frage with least answers, return None if there are no fragen with < 100 answers"""
    q = '''SELECT * from (
                SELECT 
                    fragen.id,
                    fragen.frage, 
                    fragen.downvotes as downvotes,
                    count(antworten.id) AS num_antworten 
                FROM fragen
                LEFT JOIN antworten ON antworten.frage_id=fragen.id 
                GROUP BY fragen.id)
            WHERE num_antworten < 100 AND downvotes < 3'''
    c.execute(q)
    res = c.fetchall()
    if not res:
        return
    id, fr, dv, num = random.choice(res)
    return dict(id=id, frage=fr, num=num)


@db
def len_fragen(c):
    c.execute("SELECT count(*) from fragen")
    return c.fetchone()[0]

@db
def len_antworten(c):
    return c.execute("SELECT count(*) from antworten").fetchone()[0]

print("Hello. We currently have {} questions and {} answers.".format(len_fragen(), len_antworten()))