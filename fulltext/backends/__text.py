from __future__ import absolute_import

import sys
import re

from six import StringIO


EXTENSIONS = ('txt', 'text')
BUFFER_MAX = 8192
ENCODING = sys.getfilesystemencoding()
NON_ASCII_SUB = re.compile('[\x00-\x1F\x7F-\xFF]')


def _get_file(f, **kwargs):
    buffer = StringIO()
    enc = kwargs.get('enc', ENCODING)

    while True:
        text = f.read(BUFFER_MAX)

        if not text:
            break

        try:
            text = text.decode(enc, 'replace')
        except AttributeError:
            pass
        text = NON_ASCII_SUB.sub(' ', text)
        buffer.write(text)

    return buffer.getvalue()
