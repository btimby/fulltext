# To create a postscript file for test:
# enscript -B --word-wrap -ptest.ps test.txt

from __future__ import absolute_import
from fulltext.util import run, assert_cmd_exists
from fulltext import BaseBackend


class Backend(BaseBackend):

    def check(self):
        assert_cmd_exists('pstotext')

    def handle_fobj(self, f):
        out = run('pstotext', '-', stdin=f)
        return self.decode(out)

    def handle_path(self, path):
        out = run('pstotext', path)
        return self.decode(out)
