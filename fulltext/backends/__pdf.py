from __future__ import absolute_import

import os

from fulltext.util import run, assert_cmd_exists
from fulltext import BaseBackend
from fulltext.util import is_file_path


def cmd(path, **kwargs):
    cmd = ['pdftotext']

    if kwargs.get('layout', None):
        cmd.append('-layout')

    cmd.extend([path, '-'])

    return cmd


class Backend(BaseBackend):

    def check(self):
        assert_cmd_exists('pdftotext')
        if "FULLTEXT_TESTING" in os.environ:
            assert_cmd_exists('pdfinfo')

    def handle_fobj(self, f):
        out = run(*cmd('-', **self.kwargs), stdin=f)
        return self.decode(out)

    def handle_path(self, path):
        out = run(*cmd(path, **self.kwargs))
        return self.decode(out)

    def handle_title(self, f):
        if is_file_path(f):
            # Doesn't work with file objs.
            bout = run("pdfinfo", f)
            out = self.decode(bout)
            for line in out.split("\n"):
                if line.startswith("Title:"):
                    return line.partition("Title:")[2].strip()
