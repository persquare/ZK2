import tomllib
from pathlib import Path

try:
    config_path = Path.home() / ".zk_config"
    with config_path.open("rb") as fd:
        _conf = tomllib.load(fd)
except:
    _conf = {}

conf = {
    "notesdir": _conf.get("notesdir", "~/.zk"),
    "editor": _conf.get("editor", "/usr/bin/nano"),
    "md_cmd": _conf.get("md_cmd", ""),
}

if __name__ == '__main__':
    print(conf)

