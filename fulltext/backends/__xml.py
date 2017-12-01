from __future__ import absolute_import

import re

import bs4

from six import StringIO


def _visible(elem):
    if isinstance(elem, (bs4.element.ProcessingInstruction,
                         bs4.element.Doctype)):
        return False

    elif re.match('<!--.*-->', str(elem)):
        return False

    return True


def _get_file(f, **kwargs):
    encoding, errors = kwargs['encoding'], kwargs['encoding_errors']
    bdata = f.read()
    tdata = bdata.decode(encoding, errors)
    text, bs = StringIO(), bs4.BeautifulSoup(tdata, 'lxml')

    for elem in filter(_visible, bs.findAll(text=True)):
        text.write(elem)
        text.write(u' ')

    return text.getvalue()
