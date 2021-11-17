# md_cmd = "/usr/local/bin/markdown"

# md_cmd = "/usr/local/bin/markdown++"

# md_cmd = "/usr/local/bin/pandoc -f markdown -t html"

# md_cmd = "/Library/Frameworks/Python.framework/Versions/3.7/bin/markdown_py"


if __name__ == '__main__':
    import mdproc
    print(mdproc.render("## Hello\nåäö world!"))
