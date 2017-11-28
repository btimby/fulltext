"""
This backend is used for text files.

It attempts to read the file (which is opened in binary mode) and decode it
using the default filesystem encoding. The encoding scheme can be controlled
via the `encoding` kwarg.

Any decoding issues are ignored.
"""

from __future__ import absolute_import

import sys

from six import StringIO


EXTENSIONS = ('txt', 'text')
BUFFER_MAX = 1024 * 1024
ENCODING = sys.getfilesystemencoding()


def _get_file(f, **kwargs):
    encoding = kwargs.pop('encoding', ENCODING)
    buffer = StringIO()

    while True:
        text = f.read(BUFFER_MAX)

        if not text:
            break

        try:
            text = text.decode(encoding, 'ignore')
        except AttributeError:
            pass

        # Emulate the `strings` CLI tool.
        buffer.write(text)

    return buffer.getvalue()
