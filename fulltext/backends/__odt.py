from __future__ import absolute_import

import zipfile
from lxml import etree

from six import StringIO


def _qn(ns):
    nsmap = {
        'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
    }
    one, _, two = ns.partition(':')
    return '{{{}}}{}'.format(nsmap[one], two)


def _to_string(text, elem, encoding, errors):
    if elem.text is not None:
        try:
            text.write(elem.text.decode(encoding, errors))
        except AttributeError:
            text.write(elem.text)
    for c in elem:
        if c.tag == _qn('text:tab'):
            text.write(' ')
        elif c.tag == _qn('text:s'):
            text.write(' ')
            if c.tail is not None:
                text.write(c.tail)
        else:
            _to_string(text, c, encoding, errors)
    text.write(u'\n')


def _get_file(f, **kwargs):
    encoding, errors = kwargs['encoding'], kwargs['encoding_errors']
    text = StringIO()

    with zipfile.ZipFile(f, 'r') as z:
        with z.open('content.xml', 'r') as c:
            xml = etree.parse(c)

            for c in xml.iter():
                if c.tag in (_qn('text:p'), _qn('text:h')):
                    _to_string(text, c, encoding, errors)

    return text.getvalue()


_get_path = _get_file
