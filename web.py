import json

import mistune
from flask import Flask, render_template, request

import zk2

app = Flask(__name__)

zk = zk2.ZK('~/Dropbox/Notes')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/tags")
def tags():
    tagdata = zk.tags()
    tags = sorted([t for t,c in tagdata.items() if c > 3])
    return render_template("tags.html", tags=tags)


@app.route("/note/<note_id>")
def note(note_id):
    note = zk.note(note_id)
    res = {
        'header': note.header,
        'body': mistune.markdown(note.body)
    }
    return json.dumps(res)


@app.route("/query/")
@app.route("/query/<query_string>")
def query(query_string=''):
    key = request.args.get('key')
    rev = request.args.get('reversed') == 'true'
    zk.sort_key = key
    zk.sort_reversed = rev
    if query_string.startswith('"'):
        notes = zk.search(query_string.strip('"'))
    else:
        notes = zk.filter(query_string.split())
    return render_template("item.html", notes=(n._asdict()for n in notes))


if __name__ == '__main__':
   app.run(debug = True)
