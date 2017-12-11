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
        tfile = tempfile.mkdtemp(suffix='.html')
        run("unoconv", "-d", "presentation", "-o", tfile, "-f", "html", path)
        try:
            with open(tfile, 'rb') as f:
                return self.html_backend.handle_fobj(f)
        finally:
            os.remove(tfile)

    def handle_title(self, path):
        return self.html_backend.handle_title(path)
