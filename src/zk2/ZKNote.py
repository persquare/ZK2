import os
import re
import pwd
from datetime import datetime

from . import definitions as defs


re_header_entry = re.compile(defs.HEADER_LINE_REGEX)
re_anfang = re.compile(defs.ANFANG_REGEX)


class ZKNote(object):
    """
    A representation of a Zettelkasten note with metadata and content.

    This class provides a structured way to parse, validate, and manage notes
    from a Zettelkasten system. Notes are stored as markdown files with
    YAML-style metadata headers.

    Attributes:
        data (dict): Dictionary containing all note metadata and content.
        id (str): Unique identifier for the note, derived from the date.
        date (datetime): Creation date of the note.
        modified (datetime): Last modified date (defaults to creation date).
        author (str): Author of the note, derived from system information.
        tags (list): List of tags associated with the note.
        title (str): Title of the note, extracted from the body or header.
        body (str): Main content of the note.
        backlinks (list): List of backlinks to this note (set via set_backlinks).
    """

    def __init__(self, filepath=None):
        """
        Initialize a ZKNote instance.

        Args:
            filepath (str, optional): Path to the note file. If provided,
                the note is read from this file. Defaults to None.
        """
        super(ZKNote, self).__init__()
        self.data = {}
        if filepath:
            self.read(filepath)
        else:
            self.validate()

    def __str__(self):
        """
        Return a formatted string representation of the note.

        The output includes:
        - Header with metadata (date, author, tags, etc.)
        - The note's body content

        Returns:
            str: Formatted note string.
        """
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
        """
        Handle attribute access for note metadata.

        Delegates attribute access to the internal data dictionary.
        If the attribute is not in the predefined keys, raises an error.

        Args:
            name (str): Attribute name to access.

        Raises:
            AttributeError: If the attribute is not recognized.
        """
        if name not in defs.ALL_KEYS:
            raise AttributeError("ZKNote has no attribute '{}'".format(name))
        return self.data[name]

    def _asdict(self):
        """Return the note's data as a dictionary."""
        return self.data

    def set_backlinks(self, links):
        """
        Set backlinks for this note.

        Args:
            links (list): List of note IDs that reference this note.
        """
        self.data["backlinks"] = links

    def filepath(self, zkdir):
        """
        Generate the file path for this note.

        Args:
            zkdir (str): Base directory for Zettelkasten notes.

        Returns:
            str: Full path to the note file.
        """
        return os.path.join(os.path.expanduser(zkdir), f"zk{self.id}.md")

    def read(self, filepath):
        """
        Read and parse a note from a file.

        Args:
            filepath (str): Path to the note file.
        """
        with open(filepath, "r", encoding="utf-8") as fd:
            self.parse(fd)

    def write(self, zkdir):
        """
        Write the note to a file.

        Args:
            zkdir (str): Base directory for Zettelkasten notes.
        """
        filepath = self.filepath(zkdir)
        with open(filepath, "w", encoding="utf-8") as fd:
            print(self, file=fd, end="")

    def parse(self, file):
        """
        Parse the note's header and body from a file.

        Args:
            file: File object containing the note content.
        """
        self.parse_header(file)
        self.parse_body(file)
        self.validate()

    def validate(self):
        """
        Validate and set default values for note metadata.

        Ensures all required fields are present, with defaults:
        - DATE: Current datetime
        - ID: Derived from DATE
        - MODIFIED: Same as DATE
        - TAGS: Empty list
        - AUTHOR: Current user
        - BODY: Empty string
        """
        self.data.setdefault(defs.DATE, datetime.now())
        self.data.setdefault(defs.ID, self.data[defs.DATE].strftime("%y%m%d%H%M%S"))
        self.data.setdefault(defs.MODIFIED, self.data[defs.DATE])
        self.data.setdefault(defs.TAGS, [])
        self.data.setdefault(defs.AUTHOR, pwd.getpwuid(os.getuid())[4])
        self.data.setdefault(defs.BODY, "")
        if not self.data.get(defs.TITLE):
            match = re_anfang.match(self.data[defs.BODY])
            self.data[defs.TITLE] = match.group(1) if match else ""

    def parse_body(self, file):
        """
        Extract the main body content of the note.

        Args:
            file: File object containing the note content.
        """
        self.data[defs.BODY] = file.read()

    def parse_header(self, file):
        """
        Parse the metadata header from the note.

        Processes lines between --- delimiters, extracting key-value pairs
        using the HEADER_LINE_REGEX pattern.

        Args:
            file: File object containing the note content.
        """
        # Skip initial lines
        header_tag = "---"
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
        """
        Process an individual header entry.

        Args:
            key (str): Header key (e.g., 'DATE', 'TITLE').
            value (str): Header value.
        """
        key = key.lower()
        if key not in defs.HEADER_KEYS:
            return
        if key in [defs.DATE, defs.MODIFIED]:
            self.data[key] = datetime.fromisoformat(value)
            return
        if key == defs.TAGS:
            self.data[key] = [t.strip(" ,") for t in value.split()]
            return
        self.data[key] = value

    def toggle_archived(self):
        """
        Toggle the 'archived' tag on this note.

        If the note is already marked as archived, removes the tag.
        Otherwise, adds the 'archived' tag to the note's tags.
        """
        if defs.ARCHIVED in self.tags:
            self.tags.remove(defs.ARCHIVED)
        else:
            self.tags.append(defs.ARCHIVED)

    def rename_tag(self, old_name, new_name):
        """
        Rename a tag on this note.

        If the 'old_name' tag is not present, do nothing.
        """
        if old_name in self.tags:
            self.tags.remove(old_name)
            self.tags.append(new_name)
            return new_name

