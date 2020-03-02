import json

import mistune
from flask import Flask, render_template, request, Markup

import zk2

global zk

app = Flask(__name__)


@app.route("/")
def index():
    val = request.args.get('filter_value', '')
    zk.rebuild_db()
    return render_template("index.html", filter_value=val)

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

   import argparse


   long_desc = """
   Create a zk-note file with some defaults filled in.
   The name of the created file matches the ID of the note, i.e.: "zk<ID>.md"

   Returns the full path to the newly created file on success.
   """

   parser = argparse.ArgumentParser(description=long_desc)

   parser.add_argument('--debug', action="store_true", default=False,
                       help='Run Flask server with debug option')

   parser.add_argument('--notesdir', default=None, type=str,
                       help="Directory of ZK notes")

   parser.add_argument('--port', default=9075,
                       help='Port to serve on')

   args = parser.parse_args()

   global zk

   zk = zk2.ZK(notesdir=args.notesdir)
   app.run(debug = args.debug, port=args.port)
