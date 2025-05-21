#!/usr/bin/env python3

# zk - create a new zettelkasten entry and return the path

import sys
import os
import argparse
import urllib.parse

import zk2

def app():

    long_desc = """
    Create a zk-note file with some defaults filled in.
    The name of the created file matches the ID of the note, i.e.: "zk<ID>.md"
    """

    parser = argparse.ArgumentParser(description=long_desc)

    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        help="Read note content from infile, use '-' for stdin (e.g. pbpaste | zk -)")

    parser.add_argument('--edit', action="store_true",
                             help='Create and open in editor (as set in config)')

    parser.add_argument('--tags', action="store_true",
                        help='Return current tag set in space separated list')

    parser.add_argument('--dir', action="store_true",
                        help="Return path to directory of ZK notes as set in config")

    args = parser.parse_args()

    config = zk2.config
    body = args.infile.read() if args.infile else None
    db = zk2.ZK()

    if args.dir:
        print(os.path.expanduser(config.notesdir))
        sys.exit(0)

    if args.tags:
        tags = db.tags(mincount=1)
        print(" ".join(tags))
        sys.exit(0)

    try:
        note_id = db.create(body)
    except Exception as err:
        sys.stderr.write(str(err)+'\n\n')
        sys.stderr.write('Error: Could not create zk-note\n')
        sys.exit(1)

    if args.edit:
        db.edit(note_id)


if __name__ == '__main__':
    app()

