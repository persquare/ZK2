# ZK2

A more generic Zettelkasten manager (server/client)  
Project page: <https://github.com/persquare/ZK2>

## tl;dr

Clone the project:
```
git clone https://github.com/persquare/ZK2.git
````

Install:
```
cd ZK2
python3 -m pip install -e .
```

Start server:
```
zk-run
```

Open browser to <http://localhost:9075>

Read up on [usage](#using_the_zk_browser)

You will want to configure the system, see [Configuration](#configuration)

Create a [launchAgent](#launchagent) to automatically launch server when logging in.

## Install

`python3 -m pip install -e .`

## Configuration <a name="configuration"></a>

The basic setup is handled by the ZK2 package's config file (`~/.zk_config`).  
You probably want to set a markdown renderer for the note body, as the default is to just wrap it in `<pre>...</pre>` tags.  
The default location for notes is `~/.zk`, but if you want to have your notes available everywhere pick a location in e.g. Dropbox or iCloud. 

Below is a template `~/.zk_config` (toml format) that you can copy and edit:
```
#
# Location of ZK-notes
#   Defaults to "~/.zk"
#
# notesdir = "~/Library/Mobile Documents/com~apple~CloudDocs/zk"
# notesdir = "~/mynotes"

#
# Editor
#   Defaults to TextEdit.app via "open -e"
#
# editor = "/usr/local/bin/mate"
# editor = "/usr/local/bin/bbedit"

#
# Markdown rendering
# If no md_cmd given, all note text is rendered in a <pre></pre> environment
# Renderer must accept markdown text on stdin and produce HTML on stdout
# NB. An absolute path is required, and paths with spaces need to be doubly quoted:
#   md_cmd = "~/bin/markdown" -- WRONG (relative path)
#   md_cmd = "/Users/me/my tools/markdown" -- WRONG (spaces in path)
#   md_cmd = "'/Users/me/my tools/markdown'" -- OK
# 
#
# md_cmd = "/usr/local/bin/markdown"
# md_cmd = "/usr/local/bin/pandoc -f markdown -t html"
# md_cmd = "/Library/Frameworks/Python.framework/Versions/Current/bin/markdown_py"
``
```

TextMate has a dedicated ZK bundle, see <https://github.com/persquare/Zettelkasten.tmbundle>

## Web server

`zk-run --port 9075`, pass `--debug` to start in debug mode. Go to <http://localhost:9075>

### LaunchAgent <a name="launchagent"></a>

`~/Library/LaunchAgents/com.github.persquare.zk2.plist`:
```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
	<dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
	<key>Label</key>
	<string>local.zettelkasten</string>
	<key>ProgramArguments</key>
	<array>
		<string>/path/to/zk-run</string>
		<string>--port</string>
		<string>9075</string>
	</array>
    <key>StandardOutPath</key>
    <string>/tmp/zk-server.stdout</string>
    <key>StandardErrorPath</key>
    <string>/tmp/zk-server.stderr</string>
	</dict>
</plist>
```

Find out `/path/to/zk-run` by typing `which zk-run` at the terminal prompt.

Use `zk-service [-h] {start,stop,restart}` to change status 

## Using the ZK Browser <a name="using_the_zk_browser"></a>

### Browser view
The browser view consists of a _note list_, a _tag cloud_, a _search bar_, and the _current note_ (the one selected in the note list).

You can edit the current note by clicking the document-and-pen icon.

You can narrow the items listed in the note list by using the tag cloud or the search bar.

### Quick filtering (tag cloud)
By clicking a tag in the tag cloud the list is reduced to those items tagged with that tag. Note that the tag cloud is initially empty as a tag doesn't show up until until it is present in at least six notes (configurable FIXME).

### Filter and search (search bar)
You can filter the notes by tags (`foo bar ...`) or by id (`@1407`), or perform a free text (`"yadda yadda`) search.
The above can be combined, but the order of must be `[tag]*["string with spaces]?[@123456789012]?`
Filtering performs partial matching on tags and ID. Thus, filtering by `@1408` will restrict results to notes from August 2014. 

### Archiving **notes**
You can _archive_ a note by clicking the trash can icon.
The tag `archived` has a special meaning: Notes tagged with `archived` will not be shown by default. 
This is useful for notes that are e.g. out-of-date but should be kept for some other reason.
Entering `archived` in the filter box to see all archived notes.

### Dragging notes references into a note being edited
Dragging a note item from _the note list_ into the body of a note being edited will insert a markdown link: `[Font metrics](zk://250418174118)`. Pressing ALT while dragging will insert a reference `[FIXME]: zk://250421153257 "Sub-, superscript and underline positioning"`.

### Backlinks
If the current note is linked from other notes, links to those notes will show up as _backlinks_ at the end of the note.

## Extras
The tool `zk` from the ZK2 package is useful in its own right, see `zk --help` for more info. 

An example of a putting `zk` to good use is to create a service that allows you to create a note from text in any application (change path to `zk` as needed)
