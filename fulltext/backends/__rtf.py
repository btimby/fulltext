from __future__ import absolute_import
from fulltext.util import run
from fulltext.util import assert_cmd_exists
from fulltext import BaseBackend


class Backend(BaseBackend):

    def check(self):
        assert_cmd_exists('unrtf')

    def strip(self, text):
        return self.decode(text.partition(b'-----------------')[2])

    def handle_fobj(self, f):
        return self.strip(
            run('unrtf', '--text', '--nopict', stdin=f))

    def handle_path(self, path):
        return self.strip(
            run('unrtf', '--text', '--nopict', path))
