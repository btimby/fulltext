"""
This backend is used for text files.

It attempts to read the file (which is opened in binary mode) and decode it
using the default filesystem encoding. The encoding scheme can be controlled
via the `encoding` kwarg.

Any decoding issues are ignored.
"""

from __future__ import absolute_import

from six import StringIO
from fulltext import BaseBackend


BUFFER_MAX = 1024 * 1024


class Backend(BaseBackend):

    def handle_fobj(self, f):
        buffer = StringIO()

        while True:
            text = f.read(BUFFER_MAX)

            if not text:
                break

            text = self.decode(text)

            # Emulate the `strings` CLI tool.
            buffer.write(text)

        return buffer.getvalue()
