from __future__ import absolute_import

import re

from bs4 import BeautifulSoup

from six import StringIO


EXTENSIONS = ('htm', 'html')


def _visible(elem):
    if elem.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False

    elif re.match('<!--.*-->', str(elem.encode('utf8'))):
        return False

    return True


def _get_file(f, **kwargs):
    text, bs = StringIO(), BeautifulSoup(f, 'lxml')

    for elem in filter(_visible, bs.findAll(text=True)):
        text.write(elem)
        text.write(u' ')

    return text.getvalue()
