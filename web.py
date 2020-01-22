import json

import mistune
from flask import Flask, render_template, request, Markup

import zk2

app = Flask(__name__)

zk = zk2.ZK()

@app.route("/")
def index():
    zk.rebuild_db()
    return render_template("index.html")

@app.route("/tags")
def tags():
    tags = zk.tags(mincount=6, sort=True)
    return render_template("tags.html", tags=tags)

@app.route("/note/<note_id>")
def note(note_id):
    note = zk.note(note_id)
    return render_template("note.html", note=note, body=Markup(mistune.markdown(note['body'])))

@app.route("/edit/<note_id>")
def edit(note_id):
    zk.edit(note_id)
    return ('', 204)

@app.route("/archive/<note_id>")
def archive(note_id):
    zk.archive(note_id)
    return ('', 204)

@app.route("/query/")
@app.route("/query/<query_string>")
def query(query_string=''):
    key = request.args.get('key', 'date')
    rev = request.args.get('reversed', 'true') == 'true'
    notes = zk.query(query_string, sort_key=key, reverse=rev)
    return render_template("item.html", notes=notes)


if __name__ == '__main__':
   app.run(debug = True, port=9075)
