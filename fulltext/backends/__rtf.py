from __future__ import absolute_import
import subprocess

from fulltext.compat import POSIX
from fulltext.util import run, assert_cmd_exists, exiftool_title
from fulltext.util import BaseBackend


class Backend(BaseBackend):

    def check(self, title):
        assert_cmd_exists('unrtf')
        if title:
            assert_cmd_exists('exiftool')

    def strip(self, text):
        return self.decode(text.partition(b'-----------------')[2])

    if POSIX:
        def handle_fobj(self, f):
            return self.strip(
                run('unrtf', '--text', '--nopict', stdin=f))

    def handle_path(self, path):
        cmd = ['unrtf', '--text', '--nopict', path]
        if POSIX:
            return self.strip(run(*cmd))
        else:
            # On Windows unrtf.exe prints a lot of cruft to stderr.
            # We trim it out.
            out = subprocess.check_output(cmd, stderr=subprocess.PIPE)
            return self.strip(out)

    def handle_title(self, f):
        return exiftool_title(f, self.encoding, self.encoding_errors)
