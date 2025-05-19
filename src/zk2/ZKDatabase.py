import os
import re
import subprocess
from collections import namedtuple, defaultdict

from zk2.ZKNote import ZKNote
from . import definitions as defs
from . import config

# File format:
# 0. Tagline
#    Optional: <!-- ZK<optional string> -->
# 1. Header (enclosed in '---')
#    Mandatory: Date, ID
#    Optional: Author, Modified, Tags, Title
#    Example:
#           ---
#           Date: 2019-02-10 16:22:16
#           Modified: 2019-02-11 18:24:10
#           Author: Per Persson
#           ID: 190210162216
#           Tags: zk, howto
#           Title: Linking notes
#           ---
#
# 2. Blank line(s)
#
# 3. Markdown formatted text

# File type:
# 1. zkXXXXXX.md (compatible with any editor)

#
# The note_factory used by the ZK class hides the actual implementation (object/tuple)
#
note_factory = ZKNote

re_zk_link = re.compile(defs.ZK_LINK_REGEX)
re_query = re.compile(defs.ZK_QUERY_REGEX)


#
# ZK class to query note collection
#
class ZK(object):
    """docstring for ZK"""

    sort_options = {
        defs.DATE: lambda x: x.date,
        defs.MODIFIED: lambda x: x.modified,
        defs.TITLE: lambda x: x.title,
    }

    # config = get_config()

    def __init__(self, notesdir=None):
        super(ZK, self).__init__()
        self.zkdir = os.path.expanduser(notesdir or config.conf["notesdir"])
        self._sort_key = defs.DATE
        # FIXME: Use transient sort_key and sort_reversed
        self._sort_fn = self.sort_options[self._sort_key]
        self.sort_reversed = True
        self.rebuild_db()

    def _welcome_note(self):
        welcome = ZKNote()
        welcome.data[defs.TITLE] = "Welcome!"
        welcome.data[defs.TAGS] = ["howto", "workflow"]
        # with open('../../README.md') as fd:
        #     body = fd.read()
        body = "Hello world!"
        welcome.data[defs.BODY] = body
        welcome.write(self.zkdir)

    def _maybe_init_db(self):
        try:
            os.makedirs(self.zkdir)
        except FileExistsError:
            pass
        if not os.listdir(self.zkdir):
            self._welcome_note()

    def rebuild_db(self):
        self._notes = []
        self._maybe_init_db()
        self.load_notes(self.zkdir)

    @property
    def sort_key(self):
        return self._sort_key

    @sort_key.setter
    def sort_key(self, key):
        key = key.lower()
        try:
            self._sort_fn = self.sort_options[key]
            self._sort_key = key
        except KeyError:
            self.sort_key = defs.DATE

    def all_notes(self, zkdir):
        for filename in os.listdir(zkdir):
            (name, ext) = os.path.splitext(filename)
            # if ext != '.zk':
            if ext != ".md" or not name.startswith("zk"):
                continue
            notepath = os.path.join(zkdir, filename)
            yield notepath

    def load_notes(self, zkdir):
        self._notes = [note_factory(note) for note in self.all_notes(zkdir)]
        backlinks = defaultdict(list)
        for note in self._notes:
            match = re_zk_link.findall(note.body)
            for m in match:
                backlinks[m].append(
                    {"url": f"zk://{note.id}", "title": f"{note.title}"}
                )
        for note in self._notes:
            note.set_backlinks(backlinks.get(f"zk://{note.id}", []))

    def query(self, query_string, sort_key=defs.DATE, reverse=True):
        self.sort_key = sort_key
        self.sort_reversed = reverse
        m = re_query.match(query_string)
        if not m:
            return []
        q_tags = m.group(1).rstrip().split(' ') if m.group(1) else None
        q_search = m.group(2).strip('"').strip(' ') if m.group(2) else None
        q_id = m.group(3).lstrip('@').rstrip(' ') if m.group(3) else None

        tag_notes = self._filter(q_tags) if q_tags else self._notes
        search_notes = self._search(q_search) if q_search else self._notes
        id_notes = self.id_match(q_id) if q_id else self._notes

        notes = list(set.intersection(set(tag_notes), set(search_notes), set(id_notes)))
        return [n._asdict() for n in notes]

    def id_match(self, query):
        return [n for n in self._notes if n.id.startswith(query)]

    # Partial match, see https://stackoverflow.com/a/14389112
    # FIXME: Combined query expression covering all kinds
    # Argument query is list of (possibly partial) tags
    # Empty list matches everything
    def _filter(self, query):
        if len(query) == 1 and query[0] == "untagged":
            # Return untagged notes
            r = [n for n in self._notes if not n.tags]
        else:
            # Match against tags in query
            r = []
            for n in self._notes:
                # Skip notes tagged with ARCHIVED unless ARCHIVED is part of query
                if defs.ARCHIVED in n.tags and defs.ARCHIVED not in query:
                    continue
                for q in query:
                    if any(t for t in n.tags if t.lower().startswith(q.lower())):
                        continue
                    else:
                        break
                else:
                    r.append(n)
        r = sorted(r, key=self._sort_fn, reverse=self.sort_reversed)
        return r

    def filter(self, query):
        r = self._filter(query)
        return [n._asdict() for n in r]

    def _search(self, query):
        # Body text search using regexp
        query_re = re.compile(query, re.IGNORECASE)
        r = [
            n
            for n in self._notes
            if (defs.ARCHIVED not in n.tags) and query_re.search(n.body)
        ]
        r = sorted(r, key=self._sort_fn, reverse=self.sort_reversed)
        return r

    def search(self, query):
        # Body text search using regexp
        r = self._search(query)
        return [n._asdict() for n in r]

    def note(self, note_id):
        for n in self._notes:
            if n.id == note_id:
                return n._asdict()

    def filepath(self, note_id):
        for n in self._notes:
            if n.id == note_id:
                return n.filepath(self.zkdir)

    def tags(self, mincount, sort=True):
        # Return all tags and corresponding occurence count
        tags = {}
        for n in self._notes:
            for t in n.tags:
                tags[t] = tags.setdefault(t, 0) + 1
        taglist = [t for t, c in tags.items() if c >= mincount]
        tags = sorted(taglist) if sort else taglist
        return tags

    def create(self, body=""):
        note = ZKNote()
        note.write(self.zkdir)
        # FIXME: Update should suffice...
        self.load_notes(self.zkdir)
        return note.id

    def edit(self, note_id):
        filepath = self.filepath(note_id)
        editor_cmd = f'{config.conf["editor"]} "{filepath}"'
        # os.environ['TM_TAGS']=",".join(self.tags(mincount=1))
        subprocess.run(editor_cmd, shell=True)

    def archive(self, note_id):
        filepath = self.filepath(note_id)
        note = ZKNote(filepath)
        note.toggle_archived()
        note.write(self.zkdir)


if __name__ == "__main__":
    import sys

    print(sys.version)
    note = ZKNote()
    print(note)

    note = ZKNote("tests/data/zk190912143019.md")
    print(note)

    note.write("tests/output")
