import sqlite3
import random
from pathlib import Path

from config import DB_PATH, IMPORT_FROM_FILES, IMPORT_PATH

DB_NAME = DB_PATH

REPLACE = ["-", " ", "!", "?", ":)", ";-)", ";)"]


def get_database(
    db_path=DB_PATH, import_from_files=IMPORT_FROM_FILES, import_path=IMPORT_PATH
):

    db = Database(db_path)

    if not db_path.is_file():
        print("DB does not exist, creating.")
        db.setup()

        importfiles = [f for f in Path(import_path).iterdir() if f.is_file()]

        if importfiles and import_from_files:
            print(
                "{} Import files found. Clearing DB and read them.".format(
                    len(importfiles)
                )
            )
            db.clear()
            for fn in importfiles:
                with open(Path(import_path) / fn, "r") as importfile:
                    data = importfile.read().splitlines()
                    question = data[0]
                    frage_id = add_frage(question)
                    answers = data[1:]
                    for answer in answers:
                        answer = answer.strip()
                        if not answer:
                            continue
                        num = int(answer[: answer.find(",")])
                        answertxt = answer[answer.find(",") + 1 :]
                        for x in range(num):
                            add_antwort(frage_id, answertxt)
                    set_ready(frage_id)
            print(
                "Hello. We currently have {} questions and {} answers.".format(
                    len_fragen(), len_antworten()
                )
            )

    return db


class DB:
    """
    This contextmanager eases the database access. It returns a 
    cursor to the DB given upon initialization.

    Example:

    with DB("database.db") as c:
        c.execute('''DROP DATABASE''')
    """

    def __init__(self, db_filename):
        self.db_filename = db_filename

    def __enter__(self):
        self.db = sqlite3.connect(self.db_filename)
        c = self.db.cursor()
        return c

    def __exit__(self, *args):
        self.db.commit()
        self.db.close()


class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.db = DB(self.db_path)

    def setup(self):
        with self.db as c:
            c.execute(
                """
                CREATE TABLE fragen (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                frage TEXT,
                downvotes INTEGER,
                prio INTEGER default 0,
                status TEXT default "")"""
            )
            c.execute(
                """
                CREATE TABLE antworten (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    antwort TEXT, 
                    frage_id INTEGER, 
                FOREIGN KEY (frage_id) REFERENCES fragen(id))"""
            )

    def add_frage(self, frage):
        with self.db as c:
            c.execute("INSERT INTO fragen (frage, downvotes) VALUES (?, 0)", (frage,))
            return c.lastrowid

    def add_downvote(self, frage_id):
        with self.db as c:
            c.execute(
                """UPDATE fragen SET downvotes=(
                           SELECT downvotes+1 
                           FROM fragen 
                           WHERE id=(?)
                       ) 
                           WHERE id=(?)""",
                (frage_id, frage_id),
            )

    def add_antwort(self, frage_id, antwort):
        with self.db as c:
            c.execute("SELECT downvotes FROM fragen WHERE id=(?)", (frage_id,))
            res = c.fetchone()
            if res[0] > 0:
                c.execute(
                    """UPDATE fragen 
                            SET downvotes=(
                                SELECT downvotes-1 
                                FROM fragen 
                                WHERE id=(?)) 
                                WHERE id=(?)""",
                    (frage_id, frage_id),
                )
            c.execute(
                "INSERT INTO antworten (frage_id, antwort) VALUES (?, ?)",
                (frage_id, antwort),
            )

    def get_frage(self, already_asked_ids):
        """
        Returns frage with least answers, return None if there are no fragen with < 100 answers
        """
        q = """SELECT * from (
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
                ORDER BY prio DESC, num_antworten DESC""" % (
            str(list(already_asked_ids)).replace("[", "").replace("]", "")
        )
        with self.db as c:
            c.execute(q)
            res = c.fetchone()
            if not res:
                return
            id, fr, dv, pr, num = res
            return dict(id=id, frage=fr, num=num)

    def get_finished_frage(self):
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
        with self.db as c:
            c.execute(q)
            res = c.fetchone()
            if res:
                return res
            return

    def get_frage_by_id(self, id):
        with self.db as c:
            c.execute("SELECT id, frage FROM fragen WHERE id=(?)", (id,))
            res = c.fetchone()
            if res:
                return res
            return

    def get_ready_state_by_id(self, id):
        with self.db as c:
            c.execute("SELECT status FROM fragen WHERE id=(?)", (id,))
            res = c.fetchone()
            if res:
                return res
            return

    def list_fragen(self):
        with self.db as c:
            c.execute("SELECT * FROM fragen")
            return c.fetchall()

    def get_ready_fragen(self):
        with self.db as c:
            c.execute("SELECT id, frage FROM fragen WHERE status='ready'")
            return c.fetchall()

    def get_antworten(self, question_id):
        return self.get_answers(self, question_id)

    def get_answers(self, question_id):
        q = """SELECT id, antwort from antworten WHERE frage_id=(?)"""
        with self.db as c:
            c.execute(q, (frage_id,))
            return c.fetchall()

    def update_antwort(self, id_, new_antwort):
        return self.update_answer(id_, new_antwort)

    def update_answer(self, id_, new_answer):
        q = """UPDATE antworten SET antwort=(?) WHERE id=(?)"""
        with self.db as c:
            c.execute(q, (new_answer, id_))

    def set_ready(self, id_):
        q = """UPDATE fragen SET status="ready" WHERE id=(?)"""
        with self.db as c:
            c.execute(q, (id_,))

    def unset_ready(self, id_):
        q = """UPDATE fragen SET status=NULL WHERE id=(?)"""
        with self.db as c:
            c.execute(q, (id_,))

    def get_stats(self):
        q = """SELECT * from (
                SELECT 
                fragen.id,
                fragen.frage, 
                fragen.downvotes as downvotes,
                count(antworten.id) AS num_antworten 
            FROM fragen
            LEFT JOIN antworten ON antworten.frage_id=fragen.id 
            GROUP BY fragen.id)
        ORDER BY num_antworten DESC"""
        with self.db as c:
            c.execute(q)
            return c.fetchall()

    def len_fragen(self):
        with self.db as c:
            c.execute("SELECT count(*) from fragen")
            return c.fetchone()[0]

    def clear(self):
        with self.db as c:
            c.execute("DELETE FROM fragen")
            c.execute("DELETE FROM antworten")

    def len_antworten(self):
        with self.db as c:
            return c.execute("SELECT count(*) from antworten").fetchone()[0]


def normalize(answer):
    answer = answer.lower().strip()
    for sc in REPLACE:
        answer = answer.replace(sc, "")
    return answer


def normalized_antworten(frage_id):
    antworten = get_antworten(frage_id)

    processed_antworten = dict()

    for id, antwort in antworten:
        norm_ant = normalize(antwort)
        if norm_ant not in processed_antworten:
            processed_antworten[norm_ant] = dict(antwort=antwort, count=1, ids=[id])
        else:
            processed_antworten[norm_ant]["count"] += 1
            processed_antworten[norm_ant]["ids"].append(id)

    res = []
    for pa in processed_antworten.items():
        res.append((pa[1]["count"], pa[1]))

    ants = []
    pi = 0
    for r in reversed(sorted(res, key=lambda x: x[0])):
        pi += 1
        a = r[1]
        a["platz"] = pi
        ants.append(a)
    return ants
