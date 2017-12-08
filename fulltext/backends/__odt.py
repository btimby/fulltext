from __future__ import absolute_import

import os
import zipfile
from lxml import etree

from six import StringIO

from fulltext import BaseBackend
from fulltext.util import run, assert_cmd_exists
from fulltext import is_path_str


def qn(ns):
    nsmap = {
        'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
    }
    one, _, two = ns.partition(':')
    return '{{{}}}{}'.format(nsmap[one], two)


def to_string(text, elem):
    if elem.text is not None:
        text.write(elem.text)
    for c in elem:
        if c.tag == qn('text:tab'):
            text.write(' ')
        elif c.tag == qn('text:s'):
            text.write(' ')
            if c.tail is not None:
                text.write(c.tail)
        else:
            to_string(text, c)
    text.write(u'\n')


class Backend(BaseBackend):

    def check(self):
        if "FULLTEXT_TESTING" in os.environ:
            assert_cmd_exists('exiftool')

    def handle_fobj(self, f):
        text = StringIO()

        with zipfile.ZipFile(f, 'r') as z:
            with z.open('content.xml', 'r') as c:
                xml = etree.parse(c)

                for c in xml.iter():
                    if c.tag in (qn('text:p'), qn('text:h')):
                        to_string(text, c)

        return text.getvalue()

    handle_path = handle_fobj

    def handle_title(self, f):
        if is_path_str(f):
            out = run("exiftool", "-title", f)
            out = self.decode(out).strip()
            if out:
                return out[out.find(':') + 1:].strip() or None
