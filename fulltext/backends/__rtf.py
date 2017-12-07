from __future__ import absolute_import
from fulltext.util import run
from fulltext.util import assert_cmd_exists
from fulltext import BaseBackend


def strip(text, encoding, errors):
    return text.partition(b'-----------------')[2].decode(encoding, errors)


class Backend(BaseBackend):

    def check(self):
        assert_cmd_exists('unrtf')

    def handle_fobj(self, f):
        encoding, errors = self.encoding, self.encoding_errors
        return strip(run('unrtf', '--text', '--nopict', stdin=f),
                     encoding, errors)

    def handle_path(self, path):
        encoding, errors = self.encoding, self.encoding_errors
        return strip(run('unrtf', '--text', '--nopict', path),
                     encoding, errors)
