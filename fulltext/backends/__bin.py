from __future__ import absolute_import

import re
import string

from six import StringIO

try:
    from string import maketrans

    def bytes(chars):
        return ''.join(map(chr, chars))

except ImportError:
    maketrans = bytes.maketrans


BUFFER_MAX = 1024 * 1024

# Translate printable chars to themselves and anything else to a space.
TRANSLATE = (
    bytes([i for i in range(256)]),
    bytes([i if chr(i) in string.printable else 32 for i in range(256)])
)
TRANSLATE = maketrans(*TRANSLATE)

STRIP_PUNCTUATION = re.compile(
    r'\W*\w*[!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~]{2,}\w*\W*')


def _get_file(f, **kwargs):
    buffer = StringIO()

    while True:
        text = f.read(BUFFER_MAX)

        if not text:
            break

        # Emulate the `strings` CLI tool.
        text = text.translate(TRANSLATE)
        text = text.decode('ascii', 'ignore')

        # Remove any "words" that consist mainly of punctuation.
        text = STRIP_PUNCTUATION.sub(' ', text)

        buffer.write(text)

    return buffer.getvalue()
