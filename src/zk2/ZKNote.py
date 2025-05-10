import os
import re
import pwd
from datetime import datetime

from . import definitions as defs


re_header_entry = re.compile(defs.HEADER_LINE_REGEX)
re_anfang = re.compile(defs.ANFANG_REGEX)
re_zk_link = re.compile(defs.ZK_LINK_REGEX)


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
        if name not in defs.ALL_KEYS:
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
        self.data.setdefault(defs.DATE, datetime.now())
        self.data.setdefault(defs.ID, self.data[defs.DATE].strftime("%y%m%d%H%M%S"))
        self.data.setdefault(defs.MODIFIED, self.data[defs.DATE])
        self.data.setdefault(defs.TAGS, [])
        self.data.setdefault(defs.AUTHOR, pwd.getpwuid(os.getuid())[4])
        self.data.setdefault(defs.BODY, '')
        if not self.data.get(defs.TITLE):
            match = re_anfang.match(self.data[defs.BODY])
            self.data[defs.TITLE] = match.group(1) if match else ''

    def parse_body(self, file):
        self.data[defs.BODY] = file.read()

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
        if key not in defs.HEADER_KEYS:
            return
        if key in [defs.DATE, defs.MODIFIED]:
            self.data[key] = datetime.fromisoformat(value)
            return
        if key == defs.TAGS:
            self.data[key] = [t.strip(' ,') for t in value.split()]
            return
        self.data[key] = value

    def toggle_archived(self):
        if defs.ARCHIVED in self.tags:
            self.tags.remove(defs.ARCHIVED)
        else:
            self.tags.append(defs.ARCHIVED)

