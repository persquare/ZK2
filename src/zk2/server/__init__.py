import flask
import markupsafe

import zk2

from . import mdproc

def create_app(test_config=None):
    app = flask.Flask(__name__, instance_relative_config=True)

    zk = zk2.ZK()

    @app.route("/")
    def index():
        val = flask.request.args.get('filter_value', '')
        zk.rebuild_db()
        return flask.render_template("index.html", filter_value=val)

    @app.route("/tags")
    def tags():
        tags = zk.tags(mincount=6, sort=True)
        return flask.render_template("tags.html", tags=tags)

    def _render(note_id, template):
        note = zk.note(note_id)
        content = markupsafe.Markup(mdproc.render(note['body']))
        # content = markupsafe.Markup("<pre>Foo</pre>")
        return flask.render_template(template, note=note, body=content)

    @app.route("/note/<note_id>")
    def note(note_id):
        return _render(note_id, "note.html")

    @app.route("/peek/<note_id>")
    def peek(note_id):
        return _render(note_id, "peek.html")

    @app.route("/new")
    def create():
        note_id = zk.create()
        zk.edit(note_id)
        return ('', 204)

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
        key = flask.request.args.get('key', 'date')
        rev = flask.request.args.get('reversed', 'true') == 'true'
        notes = zk.query(query_string, sort_key=key, reverse=rev)
        return flask.render_template("item.html", notes=notes)

    @app.route("/img/<path:name>")
    def img(name):
        return flask.send_from_directory(f"{zk.zkdir}/img", name)

    return app

# if __name__ == '__main__':
#
#    import argparse
#
#
#    long_desc = """
#    Serve a ZK "database"
#    """
#
#    parser = argparse.ArgumentParser(description=long_desc)
#
#    parser.add_argument('--debug', action="store_true", default=False,
#                        help='Run Flask server with debug option')
#
#    parser.add_argument('--notesdir', default=None, type=str,
#                        help="Directory of ZK notes")
#
#    parser.add_argument('--port', default=9075,
#                        help='Port to serve on')
#
#    args = parser.parse_args()
#
#    global zk
#
#    zk = zk2.ZK(notesdir=args.notesdir)
#    app.run(debug = args.debug, port=args.port)
