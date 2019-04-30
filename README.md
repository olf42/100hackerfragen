# 100hackerfragen

> A multiplayer quizshow game, like the famous "Familienduell" known from german TV since the early nineteens.

It consists of the following:

* A tool to gather questions and answers from the public via a styled web form. (fragenfragen-web.py)
* A tool to edit answers (merge typos etc.) and to cheat. (fragen-verwalter.py)
* A Small web interface to control the game
* The Game itself, full screen graphics with keyboard control. (game-web.py)

**Requirements:**

* A system to play the game (raspi might be too slow) with Linux and python >= 3.6, and possibly some other standard stuff installed.


## Installation

First, clone the repo and cd into it.

```bash
git clone https://github.com/Eigenbaukombinat/100hackerfragen.git
cd 100hackerfragen/
```

Create a python 3 virtualenv inside the cloned repo.

```bash
python3 -m venv .
```

Finally install all the dependencies (flask, pygame and a few other).

```bash
bin/pip install -r requirements.txt
```

## Game preparation

Questions and answers are collected in a local sqlite3 db. The example database.db already contains the schema and 2 sample questions with answers.

You can either use the included data collection webapp to gather additional data from the public, and use the included fragenverwalter webapp to correct then (merge typos etc.), or just start from plain .txt files.

### Basic setup with data in flat files.

If there is no database.db found, the data from all *.txt files inside the import/ directory is automatically imported into new database. Just put the question in the first line, and add answers to the following lines, in the following format:

`<number_of_answers>, <answer>`

Example:

```
Was war dein erster Heimcomputer?
23,C64
17,Amiga 500
3,Atari ST
```

> Remember deleting your database.db is required if you change the content of your import-directory!

Skip to "Play the Game" if you don't need any question collection and management.

### Gather your own questions from the public

fragenfragen-web.py contains a small web app to gather questions and answers from the public. (You might want to deploy this part on a server with a proper front-end like nginx.)

To simply run the webserver on your local host, do this:

```bash
FLASK_APP=fragenfragen-web.py bin/flask run
```

Then point a browser to http://localhost:5000 where you can answer all "open" questions (questions with < 100 answers, and not set to "ready" via fragenverwalter).

Users are also able to downvote questions, which no longer get displayed after there are 3 downvotes are reached (every answer inbetween will cancel one downvote!).

### Manage your gathered data.

At some point you may want to clean up the data. Use the 

Runs a webserver with a small application which allows to gather new questions and answers from the public.

You can start it with:

```bash
FLASK_APP=fragen-verwalter.py bin/flask run
```

Pointing your browser to http://localhost:5000 will display a list of all questions. Clicking on then opens the editor where you can merge questions by filling in the new question text on top and choose which questions to merge with.

You can not use this to add new answers.

Also choose which questions appear in the game control later, by setting them to "FERTIG".

## Play the game

XXX

