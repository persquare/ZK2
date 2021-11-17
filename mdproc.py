import subprocess
import shlex

try:
    from config import md_cmd
except:
    md_cmd = ''


def render(text):
    r = Renderer()
    return r.process(text)


class Renderer(object):
    """docstring for Renderer"""
    def __init__(self):
        self.cmd = shlex.split(md_cmd.strip())

    def process(self, text):
        return self._process(text) if self.cmd else self._default_process(text)

    def _process(self, text):
        result = subprocess.run(self.cmd, input=text, capture_output=True, encoding='utf8')
        return result.stdout if result.returncode == 0 else self._default_process(text)

    def _default_process(self, text):
        return f'<pre class="default-pre">\n{text}\n</pre>'

