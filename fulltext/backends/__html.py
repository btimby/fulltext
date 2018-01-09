from __future__ import absolute_import

import re

from bs4 import BeautifulSoup

from six import StringIO
from six import PY3

from fulltext.util import BaseBackend


class Backend(BaseBackend):

    def setup(self):
        self.bs = None

    def is_visible(self, elem):
        if elem.parent.name in ['style', 'script', '[document]', 'head']:
            return False

        if not PY3:
            elem = elem.encode(self.encoding, self.encoding_errors)
        if re.match('<!--.*-->', elem):
            return False

        return True

    def handle_fobj(self, f):
        data = f.read()
        data = self.decode(data)
        text, self.bs = StringIO(), BeautifulSoup(data, 'lxml')

        for elem in self.bs.findAll(text=True):
            if self.is_visible(elem):
                text.write(elem)
                text.write(u' ')

        return text.getvalue()

    def handle_title(self, f):
        # Title may be undefined (None), if the <title> tag is not present.
        return getattr(self.bs.title, 'string', None)
