from __future__ import absolute_import
from fulltext.util import run, assert_cmd_exists
from fulltext import BaseBackend


def cmd(path, **kwargs):
    cmd = ['pdftotext']

    if kwargs.get('layout', None):
        cmd.append('-layout')

    cmd.extend([path, '-'])

    return cmd


class Backend(BaseBackend):

    def check(self):
        assert_cmd_exists('pdftotext')

    def handle_fobj(self, f):
        out = run(*cmd('-', **self.kwargs), stdin=f)
        return self.decode(out)

    def handle_path(self, path):
        out = run(*cmd(path, **self.kwargs))
        return self.decode(out)
