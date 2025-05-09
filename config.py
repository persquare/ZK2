#
# Location of ZK-notes
#   Defaults to "~/.zk"
#   Can be overridden on commandline when starting server)
#
notesdir = "~/Library/Mobile Documents/com~apple~CloudDocs/zk"
# notesdir = "~/mynotes"

#
# Editor
#   Defaults to "/usr/bin/nano"
#
editor = "/usr/local/bin/mate"
# editor = "/usr/local/bin/bbedit"

#
# Markdown rendering
# If no md_cmd given, all note text is rendered in a <pre></pre> environment
#
# md_cmd = "/Library/Frameworks/Python.framework/Versions/3.10/bin/markdown++"
# md_cmd = "/usr/local/bin/markdown"
md_cmd = "/usr/local/bin/pandoc -f markdown -t html"
# md_cmd = "/Library/Frameworks/Python.framework/Versions/Current/bin/markdown_py"


if __name__ == '__main__':
    import mdproc
    print(mdproc.render("## Hello\nåäö world!"))
