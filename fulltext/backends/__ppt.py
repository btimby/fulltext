from __future__ import absolute_import

import os
import tempfile

from fulltext.backends.__html import Backend as HTMLBackend
from fulltext import BaseBackend
from fulltext.util import assert_cmd_exists
from fulltext.util import run


class Backend(BaseBackend):

    def check(self, title):
        assert_cmd_exists('unoconv')

    def setup(self):
        self.html_backend = HTMLBackend(
            self.encoding, self.encoding_errors, self.kwargs)

    def handle_path(self, path):
        fd, tfile = tempfile.mkstemp(suffix='.html')
        try:
            run("unoconv", "-d", "presentation",
                "-o", tfile, "-f", "html", path)
            with open(tfile, 'rb') as f:
                return self.html_backend.handle_fobj(f)
        finally:
            os.close(fd)
            os.remove(tfile)

    def handle_title(self, path):
        return self.html_backend.handle_title(path)
