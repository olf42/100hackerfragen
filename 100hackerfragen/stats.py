#!/usr/bin/env python3
"""
Displays all questions with the No. of 
answers and downvotes.
"""
from dbhandler import get_database

F_LIMIT = 100


class QuestionStats:

    def __init__(self, db, f_limit=F_LIMIT):
        self.db = db
        self.f_limit=f_limit

    def get(self):
        self.n_downvoted = 0
        self.n_finished = 0
        self.n_open = 0

        for id_, frage, downvotes, answers in db.get_stats():
            if downvotes >= 3:
                self.n_downvoted += 1
                continue
            if answers >= self.f_limit:
                self.n_finished += 1
            else:
                self.n_open += 1
            yield(id_, answers, downvotes, frage)

def show_question_stats(db, f_limit=F_LIMIT):

    qs = QuestionStats(db, f_limit)

    for id_, n_answers, n_downvotes, question_text in qs.get():
        print(f"{id_}\t{n_answers}\t{n_downvotes}\t{question_text}")

    print("Downvoted: {}".format(qs.n_downvoted))
    print("Finished: {}".format(qs.n_finished))
    print("Open: {}".format(qs.n_open))

if __name__ == "__main__":
    db = get_database(import_from_files=True, import_path="./import")
    show_question_stats(db)
