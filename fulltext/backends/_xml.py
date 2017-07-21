from __future__ import absolute_import

from lxml import etree

from fulltext.util import StringIO


EXTENSIONS = ('xml',)


def _get_file(f, **kwargs):
    text, root = StringIO(), etree.parse(f)
    for elem in root.iter():
        text.write(unicode(elem.text, 'utf8'))
        text.write(u' ')
    return text.getvalue()
