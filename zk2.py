# File format:
# 1. Header
#    Mandatory: Date, ID
#    Optional: Author, Modified, Tags, Title
#    Example:
#           Date: 2019-02-10 16:22:16
#           Modified: 2019-02-11 18:24:10
#           Author: Per Persson
#           ID: 190210162216
#           Tags: zk, howto
#           Title: Linking notes
#
# 2. Blank line(s)
#
# 3. Markdown formatted text

# File type:
# 1. zkXXXXXX.md (compatible with any editor)
# 2. XXXXXX.zk (can have special grammar with markdown injection)

import os
import re
import subprocess
import shutil
from datetime import datetime
from collections import namedtuple


AUTHOR = 'author'
DATE = 'date'
ID = 'id'
MODIFIED = 'modified'
TAGS = 'tags'
TITLE = 'title'

ORDER = [DATE, MODIFIED, ID, AUTHOR, TAGS, TITLE]


HEADER_LINE_REGEX = r'^([a-zA-Z][a-zA-Z0-9_]*):\s*(.*)\s*'
ANFANG_REGEX = r'^((?:\S+\s+){1,6})'

re_header_entry = re.compile(HEADER_LINE_REGEX)
re_anfang = re.compile(ANFANG_REGEX)


# FIXME: 
# - Add file path
# - Remove unnecessary properties

class ZKNote(object):
    """docstring for ZKNote"""
    def __init__(self, filepath):
        super(ZKNote, self).__init__()
        with open(filepath, 'r', encoding='utf-8') as fd:
            self.parse(fd)
        self.filepath = filepath

    def __str__(self):
        return ' : '.join((self.date_string, self.title, self.tags_string))

    def set_header(self, header):
        tag_str = header.get(TAGS, '')
        tags = sorted([t.strip(' ,') for t in tag_str.split()])
        header[TAGS] = tags
        self._header = header

    @property
    def id(self):
        return self._header[ID]

    @property
    def date_string(self):
        return self._header.get(DATE, '')

    @property
    def date(self):
        try:
            return datetime.fromisoformat(self.date_string)
        except:
            return datetime.min

    @property
    def modified_string(self):
        return self._header.get(MODIFIED, '')

    @property
    def modified(self):
        try:
            return datetime.fromisoformat(self.modified_string)
        except:
            return self.date

    @property
    def author(self):
        return self._header.get(AUTHOR, 'Anonymous')

    @property
    def title(self):
        return self._header.get(TITLE, '')

    @property
    def tags(self):
        return self._header.get(TAGS, [])

    @property
    def tags_string(self):
        return ', '.join(self.tags)

    @property
    def body(self):
        return self._body

    @property
    def header(self):
        entries = {key.capitalize(): self._header[key] for key in ORDER if key in self._header}
        if TAGS in self._header:
            entries[TAGS.capitalize()] = self.tags_string
        entries = ["{}: {}".format(k, v) for k, v in entries.items()]
        return '\n'.join(entries)


    def parse(self, file):
        self.set_header(self.parse_header(file))
        self._body = file.read()
        match = re_anfang.match(self._body)
        if match:
            self._header.setdefault(TITLE, match.group(1))


    def parse_header(self, file):
        header = {}
        for line in file:
            line = line.strip()
            if not line:
                return header
            match = re_header_entry.match(line)
            if match:
                header[match.group(1).lower()] = match.group(2)

#
# Using a namedtuple instead of a class speeds up filtering by a 2x factor
#
Note = namedtuple('Note', [
    'id',
    'date_string',
    'date',
    'modified_string',
    'modified',
    'author',
    'title',
    'tags',
    'tags_string',
    'body',
    'header',
    'filepath'
])

#
# Reusing the ZKNote class to parse files and populate Note namedtuple
# adds just a 10ms to startup time, so no need to write special code.
#
def create_note(filepath):
    n = ZKNote(filepath)
    note = Note(
        id=n.id,
        date_string=n.date_string,
        date=n.date,
        modified_string=n.modified_string,
        modified=n.modified,
        author=n.author,
        title=n.title,
        tags=n.tags,
        tags_string=n.tags_string,
        body=n.body,
        header=n.header,
        filepath=n.filepath)
    return note


#
# The note_factory used by the ZK class hides the actual implementation (object/tuple)
#
note_factory = create_note

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

    # FIXME: To config file
    config = {
        'notesdir': '~/Dropbox/Notes',
        'editor': 'mate',
    }
    
    def __init__(self):
        super(ZK, self).__init__()
        self.zkdir = os.path.expanduser(self.config['notesdir'])
        self._sort_key = DATE
        self._sort_fn = self.sort_options[self._sort_key]
        self.rebuild_db()
    

    def rebuild_db(self):
        self._notes = []
        self.load_notes(self.zkdir)
        self.sort_reversed = True
        self.current_id = self.filter([])[0].id

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

    # Partial match, see https://stackoverflow.com/a/14389112
    def filter(self, query):
        # Argument query is list of (possibly partial) tags
        # Empty list matches everything
        r = []
        for n in self._notes:
            for q in query:
                if any(t for t in n.tags if t.startswith(q)):
                    continue
                else:
                    break
            else:
                r.append(n)
        return sorted(r, key=self._sort_fn, reverse=self.sort_reversed)

    def search(self, query):
        # Body text search using regexp
        query_re = re.compile(query, re.IGNORECASE)
        r = [n for n in self._notes if query_re.search(n.body)]
        return sorted(r, key=self._sort_fn, reverse=self.sort_reversed)

    def note(self, note_id):
        for n in self._notes:
             if n.id == note_id:
                 return n

    def filepath(self, note_id):
        note = self.note(note_id)
        if note:
            return note.filepath
        
    def tags(self):
        # Return all tags and corresponding occurence count
        tags = {}
        for n in self._notes:
            for t in n.tags:
                tags[t] = tags.setdefault(t, 0) + 1
        return tags
        
    def edit(self, note_id):
        filepath = self.filepath(note_id)
        editor_cmd = self.config['editor']
        _ = subprocess.call(editor_cmd + " " + filepath, shell=True)

    def archive(self, note_id):
        # FIXME: Use tag 'archived' with special handling
        #        Need to be able to read/write header properly
        
        # filepath = self.filepath(note_id)
        # shutil.move(filepath, filepath+".deleted")
        print("ARCHIVE", note_id)    


if __name__ == '__main__':
    import json
    # note = note_factory('test.zk')
    # print(note.id)
    # print(note.date)
    # print(note.date_string)
    # print(note.modified)
    # print(note.modified_string)
    # print(note.author)
    # print(note.title)
    # print(note.tags)
    # print('---')
    # print(note.header)
    # print()
    # print(note.body)


    t0 = datetime.now()
    zk = ZK()
    t1 = datetime.now()
    t = (t1-t0).total_seconds()
    print("Initialized {} notes in {:.1f} ms".format(len(zk._notes), t*1000))
    zk.sort_reversed = True
    zk.sort_key = 'date'
    t0 = datetime.now()
    result = zk.filter([])
    t1 = datetime.now()
    t = (t1-t0).total_seconds()
    print("Filtered {} notes in {:.1f} ms".format(len(zk._notes), t*1000))
    # t0 = datetime.now()
    # result = zk.search(r'textmate')
    # t1 = datetime.now()
    # t = (t1-t0).total_seconds()
    # print("Searched {} notes in {:.1f} ms".format(len(zk._notes), t*1000))
    # for n in result:
    #     print(n.date, n.modified, n.title, n.tags_string)
    # # print(json.dumps(zk.tags(), indent=4))
    # print("{}\n\n{}".format(result[0].header, result[0].body))
    n = zk.note('190618132530')
    print(n.body)
    




