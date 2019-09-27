#!/usr/bin/env python3

# zk - create a new zettelkasten entry and return the path

import sys
import os
import argparse

import zk2



def create_zk(body):
    config = zk2.get_config()
    note = zk2.ZKNote()
    note.body = body or ''
    notesdir = os.path.expanduser(config['notesdir'])
    note.write(notesdir)
    return note.filepath(notesdir)

def txmt_URI(path):
    uri = f"txmt://open?url=file://{path}&line=7&column=0"
    return uri

if __name__ == '__main__':


    long_desc = """
    Create a zk-note file with some defaults filled in.
    The name of the created file matches the ID of the note, i.e.: "zk<ID>.md"

    Returns the full path to the newly created file on success.
    """

    parser = argparse.ArgumentParser(description=long_desc)

    parser.add_argument('--txmt', action="store_true",
                        help='Format output as a URI for use with TextMate 2')

    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        help="Read body text from infile, use '-' for stdin")

    args = parser.parse_args()

    body = args.infile.read() if args.infile else None

    try:
        retval = create_zk(body)
    except Exception as err:
        sys.stderr.write(str(err)+'\n\n')
        sys.stderr.write('Error: Could not create zk-note\n')
        sys.exit(1)

    if args.txmt:
        retval = txmt_URI(retval)
    print(retval)


