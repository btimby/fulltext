from __future__ import absolute_import

from lxml import etree

from six import StringIO


EXTENSIONS = ('xml',)


def _get_file(f, **kwargs):
    text, root = StringIO(), etree.parse(f)
    for elem in root.iter():
        text.write(elem.text)
        text.write(u' ')
    return text.getvalue()
