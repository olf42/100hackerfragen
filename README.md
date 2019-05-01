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

Then point a browser to http://localhost:5000 where people can answer all "open" questions (questions with < 100 answers, and not set to "ready" via fragenverwalter), and add new questions.

Users are also able to downvote questions, which no longer get displayed after there are 3 downvotes are reached (every answer inbetween will cancel one downvote!).

### Manage your gathered data.

At some point you may want to clean up the data. The included fragen-verwalter.py webapp helps you with that.

You can start it with:

```bash
FLASK_APP=fragen-verwalter.py bin/flask run
```

Pointing your browser to http://localhost:5000 will display a list of all questions. Clicking on them opens the editor where you can merge questions by filling in the new question text on top and choose which questions to merge with.

You can not use this to add new answers.

Also choose which questions appear in the game control later, by setting them to "FERTIG".

## Play the game


To play the game, first start the gameweb.py application to control display of questions and answers.

```bash
FLASK_APP=gameweb.py bin/flask run
```

Point your browser to http://localhost:5000 and select question and then the answers which should be revealed.

To access the tool from another device, run flask with `-h 0.0.0.0` parameter so that it listens on any IP (or set the correct ip which the tool should listen on). Then use http://<ip_or_host_of_your_machine>:5000 to access it.


Next, start the game by running:

```bash
bin/pythom game.py
```

Use the following keys to control it:

```
f ... Finish round
p ... Play intro music (don't press twice or fix the bug!)

1-3 start round 1-3

a ... Buzzer team A
b ... Buzzer team B
s ... silent Buzzer team A
o ... silent Buzzer team B

Backspace ... reset buzzer state

x ... team on turn answered wrong
y ... play fail sound
 
q ... quit
F11 ... toggle fullscreen

Memes (Press and hold):

d ... ccc
w ... WAT
c ... CYBER
t ... BTX
v ... putin
m ... merkel
k ... facepalm
l ... lol
n ... nyancat

4-9 ... Custom memes 1-6
```

## Troubleshooting

If you run out of luck and something goes wrong, quit the game (using q), and edit points.txt, first Line contains score of team a and second line of team b.
Then start the game again. Score should be properly set.


## Customizing

You can place custom memes in the "memes" directory in subdirectories 1-6.
Play them while in game with keys 4 to 9.

You could also replace the integrated memes with new image and sound files. They are stored in the images/ and sounds/ directory.

## TODO

* Use plugin-system for memes with config file to choose which are activted and map to keys.
* Use config for all keys. Provide example for "Buzzertisch" device.
* Better stlye for gameweb.py app (improve usability on phones).
* Provide way to log rounds, set scores, maybe "undo" via gameweb.py.

