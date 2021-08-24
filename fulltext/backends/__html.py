from __future__ import absolute_import

import re

from bs4 import BeautifulSoup

from fulltext.util import BaseBackend


class Backend(BaseBackend):

    def setup(self):
        self.bs = None

    def handle_fobj(self, f):
        data = f.read()
        data = self.decode(data)
        self.bs = BeautifulSoup(data, 'lxml')
        if self.bs.br:
            self.bs.br.replace_with('\n')
        return self.bs.text

    def handle_title(self, f):
        # Title may be undefined (None), if the <title> tag is not present.
        return getattr(self.bs.title, 'string', None)
