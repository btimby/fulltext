from __future__ import absolute_import
from fulltext.util import run, assert_cmd_exists
from fulltext import BaseBackend
from fulltext import is_path_str


def cmd(path, **kwargs):
    cmd = ['pdftotext']

    if kwargs.get('layout', None):
        cmd.append('-layout')

    cmd.extend([path, '-'])

    return cmd


class Backend(BaseBackend):

    def check(self):
        assert_cmd_exists('pdftotext')
        assert_cmd_exists('pdfinfo')

    def handle_fobj(self, f):
        out = run(*cmd('-', **self.kwargs), stdin=f)
        return self.decode(out)

    def handle_path(self, path):
        out = run(*cmd(path, **self.kwargs))
        return self.decode(out)

    def handle_title(self, f):
        if is_path_str(f):
            bout = run("pdfinfo", f)
        else:
            bout = run("pdfinfo", f, stdin=f)
        out = self.decode(bout)
        for line in out.split("\n"):
            if line.startswith("Title:"):
                return line.partition("Title:")[2].strip()
