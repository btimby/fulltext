from __future__ import absolute_import

import re

from bs4 import BeautifulSoup

from six import StringIO


def _visible(elem):
    if elem.parent.name in ['style', 'script', '[document]', 'head']:
        return False

    elif re.match('<!--.*-->', str(elem)):
        return False

    return True


def _get_file(f, **kwargs):
    encoding, errors = kwargs['encoding'], kwargs['encoding_errors']
    data = f.read()
    data = data.decode(encoding, errors)
    text, bs = StringIO(), BeautifulSoup(data, 'lxml')

    for elem in filter(_visible, bs.findAll(text=True)):
        text.write(elem)
        text.write(u' ')

    return text.getvalue()
