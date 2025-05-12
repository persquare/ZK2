# ZK2
A more generic Zettelkasten manager (server/client)

## Project
```
├── LICENSE
├── README.md
├── pyproject.toml
├── src
│   └── zk2
│       ├── ZKDatabase.py
│       ├── ZKNote.py
│       ├── __init__.py
│       ├── config.py
│       ├── definitions.py
│       ├── server
│       │   ├── __init__.py
│       │   ├── mdproc.py
│       │   ├── static
│       │   │   ├── if_back_370091.svg
│       │   │   ├── if_cloud_370088.svg
│       │   │   ├── if_delete_370086.svg
│       │   │   ├── if_eye_370084.svg
│       │   │   ├── if_globe_646196.svg
│       │   │   ├── if_note_370077.svg
│       │   │   ├── zk2.css
│       │   │   └── zk2.js
│       │   └── templates
│       │       ├── index.html
│       │       ├── item.html
│       │       ├── note.html
│       │       ├── peek.html
│       │       └── tags.html
│       ├── zk_server.py
│       └── zk_tool.py
└── zk2.todo
```


## Install

`pip install -e .`

## Configuration

`~/.zk_config` (toml format):
```
#
# Location of ZK-notes
#   Defaults to "~/.zk"
#   Can be overridden on commandline when starting server)
#
# notesdir = "~/Library/Mobile Documents/com~apple~CloudDocs/zk"
# notesdir = "~/mynotes"

#
# Editor
#   Defaults to "/usr/bin/nano"
#
# editor = "/usr/local/bin/mate"
# editor = "/usr/local/bin/bbedit"

#
# Markdown rendering
# If no md_cmd given, all note text is rendered in a <pre></pre> environment
#
# md_cmd = "/usr/local/bin/markdown"
# md_cmd = "/usr/local/bin/pandoc -f markdown -t html"
# md_cmd = "/Library/Frameworks/Python.framework/Versions/Current/bin/markdown_py"

```

## Web service

`flask --app zk2.server run --port 9075`, pass `--debug` to start in debug mode.

### LaunchAgent

`~//Library/LaunchAgents/com.github.persquare.zk2.plist`:
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
		<string>/path/to/flask</string>
		<string>--app</string>
		<string>zk2.server</string>
		<string>run</string>
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

Use `zk-server [-h] {start,stop,restart}` to change status 

## ToDo

- tmBundle
    - yaml (optional)

- extras? 
    - mermaid (howto)