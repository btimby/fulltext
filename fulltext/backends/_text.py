import sys
import re

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO


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

        text = text.decode(enc, 'replace')
        text = NON_ASCII_SUB.sub(' ', text)
        buffer.write(text)

    return buffer.getvalue()
