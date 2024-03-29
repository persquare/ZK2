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

import os
import re
import pwd
import subprocess
import shutil
from datetime import datetime
from collections import namedtuple, defaultdict


AUTHOR = 'author'
DATE = 'date'
ID = 'id'
MODIFIED = 'modified'
TAGS = 'tags'
TITLE = 'title'
ARCHIVED = 'archived'

HEADER_KEYS = [DATE, MODIFIED, ID, AUTHOR, TAGS, TITLE]

BODY = 'body'
ALL_KEYS = HEADER_KEYS + [BODY]


HEADER_LINE_REGEX = r'^([a-zA-Z][a-zA-Z0-9_]*):\s*(.*)\s*'
ANFANG_REGEX = r'^((?:\S+\s+){1,6})'
ZK_LINK_REGEX = r'zk://[0-9]{12,}'

re_header_entry = re.compile(HEADER_LINE_REGEX)
re_anfang = re.compile(ANFANG_REGEX)
re_zk_link = re.compile(ZK_LINK_REGEX)


class ZKNote(object):
    """docstring for ZKNote"""
    def __init__(self, filepath=None):
        super(ZKNote, self).__init__()
        self.data = {}
        if filepath:
            self.read(filepath)
        else:
            self.validate()

    def __str__(self):
        return f"""<!-- ZK{self.id} -->
---
Date: {self.date}
Modified: {self.modified}
Author: {self.author}
ID: {self.id}
Tags: {', '.join(self.tags)}
Title: {self.title}
---
{self.body}"""


    def __getattr__(self, name):
        if name not in ALL_KEYS:
            raise AttributeError("ZKNote has no attribute '{}'".format(name))
        return self.data[name]

    def _asdict(self):
        return self.data

    def set_backlinks(self, links):
        self.data['backlinks'] = links

    def filepath(self, zkdir):
        return os.path.join(os.path.expanduser(zkdir), f"zk{self.id}.md")

    def read(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as fd:
            self.parse(fd)

    def write(self, zkdir):
        filepath = self.filepath(zkdir)
        with open(filepath, 'w', encoding='utf-8') as fd:
            print(self, file=fd, end='')

    def parse(self, file):
        self.parse_header(file)
        self.parse_body(file)
        self.validate()

    def validate(self):
        self.data.setdefault(DATE, datetime.now())
        self.data.setdefault(ID, self.data[DATE].strftime("%y%m%d%H%M%S"))
        self.data.setdefault(MODIFIED, self.data[DATE])
        self.data.setdefault(TAGS, [])
        self.data.setdefault(AUTHOR, pwd.getpwuid(os.getuid())[4])
        self.data.setdefault(BODY, '')
        if not self.data.get(TITLE):
            match = re_anfang.match(self.data[BODY])
            self.data[TITLE] = match.group(1) if match else ''

    def parse_body(self, file):
        self.data[BODY] = file.read()

    def parse_header(self, file):
        # Skip initial lines
        header_tag = '---'
        line = ""
        while line != header_tag:
            line = file.readline().strip()

        while True:
            line = file.readline()
            line = line.strip()
            if line == header_tag:
                break
            match = re_header_entry.match(line)
            if match:
                self.parse_entry(key=match.group(1), value=match.group(2))


    def parse_entry(self, key, value):
        key = key.lower()
        if key not in HEADER_KEYS:
            return
        if key in [DATE, MODIFIED]:
            self.data[key] = datetime.fromisoformat(value)
            return
        if key == TAGS:
            self.data[key] = [t.strip(' ,') for t in value.split()]
            return
        self.data[key] = value

    def toggle_archived(self):
        if ARCHIVED in self.tags:
            self.tags.remove(ARCHIVED)
        else:
            self.tags.append(ARCHIVED)

#
# The note_factory used by the ZK class hides the actual implementation (object/tuple)
#
note_factory = ZKNote
# note_factory = create_note

def get_config():
    try:
        import config
    except:
        pass

    conf = {}

    try:
        conf['notesdir'] = config.notesdir
    except:
        conf['notesdir'] = '~/.zk'

    try:
        conf['editor'] = config.editor
    except:
        conf['editor'] = '/usr/bin/nano'

    return conf

#
# ZK class to query note collection
#
class ZK(object):
    """docstring for ZK"""

    sort_options = {
        DATE: lambda x: x.date,
        MODIFIED: lambda x: x.modified,
        TITLE: lambda x: x.title,
    }

    config = get_config()

    def __init__(self, notesdir=None):
        super(ZK, self).__init__()
        self.zkdir = os.path.expanduser(notesdir or self.config['notesdir'])
        self._sort_key = DATE
        # FIXME: Use transient sort_key and sort_reversed
        self._sort_fn = self.sort_options[self._sort_key]
        self.sort_reversed = True
        self.rebuild_db()

    def _welcome_note(self):
        welcome = ZKNote()
        welcome.data[TITLE] = "Welcome!"
        welcome.data[TAGS] = ["howto", "workflow"]
        with open('README.md') as fd:
            body = fd.read()
        welcome.data[BODY] = body
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
            self.sort_key = DATE

    def all_notes(self, zkdir):
        for filename in os.listdir(zkdir):
            (name, ext) = os.path.splitext(filename)
            # if ext != '.zk':
            if ext != '.md' or not name.startswith('zk'):
                continue
            notepath = os.path.join(zkdir, filename)
            yield notepath

    def load_notes(self, zkdir):
        self._notes = [note_factory(note) for note in self.all_notes(zkdir)]
        backlinks = defaultdict(list)
        for note in self._notes:
            match = re_zk_link.findall(note.body)
            for m in match:
                backlinks[m].append({"url":f"zk://{note.id}", "title":f"{note.title}"})
        for note in self._notes:
            note.set_backlinks(backlinks.get(f"zk://{note.id}", []))


    #
    # FIXME: Use generic query_string and combine filter/search/sort into same method
    #
    def query(self, query_string, sort_key=DATE, reverse=True):
        self.sort_key = sort_key
        self.sort_reversed = reverse
        if query_string.startswith('"'):
            notes = self.search(query_string.strip('"'))
        else:
            notes = self.filter(query_string.split())
        return notes

    # Partial match, see https://stackoverflow.com/a/14389112
    # FIXME: Combined query expression covering all kinds
    # Argument query is list of (possibly partial) tags
    # Empty list matches everything
    def filter(self, query):
        if len(query) == 1 and query[0] == 'untagged':
            # Return untagged notes
            r = [n for n in self._notes if not n.tags]
        else:
            # Match against tags in query
            r = []
            for n in self._notes:
                # Skip notes tagged with ARCHIVED unless ARCHIVED is part of query
                if (ARCHIVED in n.tags and ARCHIVED not in query):
                    continue
                for q in query:
                    if any(t for t in n.tags if t.lower().startswith(q.lower())):
                        continue
                    else:
                        break
                else:
                    r.append(n)
        r = sorted(r, key=self._sort_fn, reverse=self.sort_reversed)
        return [n._asdict() for n in r]

    def search(self, query):
        # Body text search using regexp
        query_re = re.compile(query, re.IGNORECASE)
        r = [n for n in self._notes if (ARCHIVED not in n.tags) and query_re.search(n.body)]
        r = sorted(r, key=self._sort_fn, reverse=self.sort_reversed)
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
        taglist = [t for t,c in tags.items() if c >= mincount]
        tags = sorted(taglist) if sort else taglist
        return tags

    def create(self, body=''):
        note = ZKNote()
        note.write(self.zkdir)
        # FIXME: Update should suffice...
        self.load_notes(self.zkdir)
        return note.id

    def edit(self, note_id):
        filepath = self.filepath(note_id)
        editor_cmd = f'{self.config["editor"]} "{filepath}"'
        # os.environ['TM_TAGS']=",".join(self.tags(mincount=1))
        subprocess.run(editor_cmd, shell=True)

    def archive(self, note_id):
        filepath = self.filepath(note_id)
        note = ZKNote(filepath)
        note.toggle_archived()
        note.write(self.zkdir)


if __name__ == '__main__':
    import sys
    print(sys.version)
    note = ZKNote()
    print(note)

    note = ZKNote("tests/data/zk190912143019.md")
    print(note)

    note.write("tests/output")







    # import json
    # # note = note_factory('test.zk')
    # # print(note.id)
    # # print(note.date)
    # # print(note.date_string)
    # # print(note.modified)
    # # print(note.modified_string)
    # # print(note.author)
    # # print(note.title)
    # # print(note.tags)
    # # print('---')
    # # print(note.header)
    # # print()
    # # print(note.body)
    #
    #
    # t0 = datetime.now()
    # zk = ZK()
    # t1 = datetime.now()
    # t = (t1-t0).total_seconds()
    # print("Initialized {} notes in {:.1f} ms".format(len(zk._notes), t*1000))
    # zk.sort_reversed = True
    # zk.sort_key = 'date'
    # t0 = datetime.now()
    # result = zk.filter(['zk', 'work', 'yadda'])
    # t1 = datetime.now()
    # t = (t1-t0).total_seconds()
    # print("Filtered {} notes in {:.1f} ms".format(len(zk._notes), t*1000))
    # # t0 = datetime.now()
    # # result = zk.search(r'textmate')
    # # t1 = datetime.now()
    # # t = (t1-t0).total_seconds()
    # # print("Searched {} notes in {:.1f} ms".format(len(zk._notes), t*1000))
    # # for n in result:
    # #     print(n.date, n.modified, n.title, n.tags_string)
    # # # print(json.dumps(zk.tags(), indent=4))
    # # print("{}\n\n{}".format(result[0].header, result[0].body))
    # n = zk.note('190618132530')
    # print(n.body)





