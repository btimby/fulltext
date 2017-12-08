from __future__ import absolute_import
import os

from fulltext.util import run, assert_cmd_exists, exiftool_title
from fulltext import BaseBackend


class Backend(BaseBackend):

    def check(self):
        assert_cmd_exists('unrtf')
        if "FULLTEXT_TESTING" in os.environ:
            assert_cmd_exists('pdfinfo')

    def strip(self, text):
        return self.decode(text.partition(b'-----------------')[2])

    def handle_fobj(self, f):
        return self.strip(
            run('unrtf', '--text', '--nopict', stdin=f))

    def handle_path(self, path):
        return self.strip(
            run('unrtf', '--text', '--nopict', path))

    def handle_title(self, f):
        return exiftool_title(f, self.encoding, self.encoding_errors)
