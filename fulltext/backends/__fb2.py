from __future__ import absolute_import

import re

import bs4

from six import StringIO
from six import PY3

from fulltext.util import BaseBackend


class Backend(BaseBackend):

    def setup(self):
        self.bs = None

    def is_visible(self, elem):
        if isinstance(elem, (bs4.element.ProcessingInstruction,
                             bs4.element.Doctype)):
            return False

        if elem.parent.name not in ["body", "p"]:
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
            if elem.parent.name == "empty-line":
                text.write(u"\n")
            if self.is_visible(elem):
                text.write(elem)
                text.write(u"\n")

        return text.getvalue()

    def handle_title(self, f):
        fname = ""
        s = ""
        try:
            fname = f.name
        except AttributeError:
            fname = f

        with open(fname, "r", encoding = self.encoding, errors = self.encoding_errors) as book: s = book.read()
        bs = bs4.BeautifulSoup(s, 'lxml')
        t = getattr(bs, "book-title", None)
        if t is None:
            return None
        return getattr(t, "string", None)
