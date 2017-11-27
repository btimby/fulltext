from __future__ import absolute_import

import string

from six import StringIO

try:
    from string import maketrans

    def bytes(chars):
        return ''.join(map(chr, chars))

except ImportError:
    maketrans = bytes.maketrans


BUFFER_MAX = 1024 * 1024

DELETE = bytes([
    i for i in range(256) if chr(i) not in string.printable
])
TRANSLATE = maketrans(b'\r\n', b'  ')


def _get_file(f, **kwargs):
    buffer = StringIO()

    while True:
        text = f.read(BUFFER_MAX)

        if not text:
            break

        text = text.translate(TRANSLATE, DELETE)
        text = text.decode('ascii', 'ignore')

        # Emulate the `strings` CLI tool.
        buffer.write(text)

    return buffer.getvalue()
