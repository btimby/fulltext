from __future__ import absolute_import

import re

import bs4

from six import StringIO
from six import PY3

from fulltext import BaseBackend


class Backend(BaseBackend):

    def is_visible(self, elem):
        if isinstance(elem, (bs4.element.ProcessingInstruction,
                             bs4.element.Doctype)):
            return False

        if not PY3:
            elem = elem.encode(self.encoding, self.encoding_errors)
        if re.match('<!--.*-->', elem):
            return False

        return True

    def handle_fobj(self, f):
        bdata = f.read()
        tdata = self.decode(bdata)
        text, bs = StringIO(), bs4.BeautifulSoup(tdata, 'lxml')

        for elem in bs.findAll(text=True):
            if self.is_visible(elem):
                text.write(elem)
                text.write(u' ')

        return text.getvalue()
