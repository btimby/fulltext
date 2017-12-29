from __future__ import absolute_import
import tempfile
import os

from fulltext.util import run, assert_cmd_exists
from fulltext import BaseBackend
from fulltext.util import is_file_path
from fulltext.compat import which, POSIX


def unix_cmd(path, **kwargs):
    print(which("pdftotext"))
    cmd = ['pdftotext']

    if kwargs.get('layout', None):
        cmd.append('-layout')

    cmd.extend([path, '-'])

    return cmd


class Backend(BaseBackend):

    def check(self, title):
        assert_cmd_exists('pdftotext')
        if title:
            assert_cmd_exists('pdfinfo')

    if POSIX:
        def handle_fobj(self, f):
            out = run(*unix_cmd('-', **self.kwargs), stdin=f)
            return self.decode(out)

        def handle_path(self, path):
            out = run(*unix_cmd(path, **self.kwargs))
            return self.decode(out)
    else:
        def handle_path(self, path):
            # Windows implementation.
            fd, outfile = tempfile.mkstemp(suffix='.txt')
            try:
                run("pdftotext", path, outfile)
                with open(outfile, "rb") as f:
                    text = f.read()
                return self.decode(text)
            finally:
                os.close(fd)
                os.remove(outfile)

    def handle_title(self, f):
        if is_file_path(f):
            # Doesn't work with file objs.
            bout = run("pdfinfo", f)
            out = self.decode(bout)
            for line in out.split("\n"):
                if line.startswith("Title:"):
                    return line.partition("Title:")[2].strip()
