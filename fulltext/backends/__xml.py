from __future__ import absolute_import

import re

from bs4 import BeautifulSoup

from six import StringIO


def _get_file(f, **kwargs):
    text, bs = StringIO(), BeautifulSoup(f, 'lxml')

    for elem in bs.findAll(text=True):
        text.write(elem)
        text.write(u' ')

    return text.getvalue()
