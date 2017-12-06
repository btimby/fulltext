from __future__ import absolute_import

import re

from bs4 import BeautifulSoup

from six import StringIO
from six import PY3


def _is_visible(elem, encoding, errors):
    if elem.parent.name in ['style', 'script', '[document]', 'head']:
        return False

    if not PY3:
        elem = elem.encode(encoding, errors)
    if re.match('<!--.*-->', elem):
        return False

    return True


def handle_fobj(f, **kwargs):
    encoding, errors = kwargs['encoding'], kwargs['encoding_errors']
    data = f.read()
    data = data.decode(encoding, errors)
    text, bs = StringIO(), BeautifulSoup(data, 'lxml')

    for elem in bs.findAll(text=True):
        if _is_visible(elem, encoding, errors):
            text.write(elem)
            text.write(u' ')

    return text.getvalue()
