from __future__ import absolute_import
import logging
import tempfile

import rarfile
from six import StringIO
from contextlib2 import ExitStack

from fulltext import BaseBackend, get
from fulltext.util import memoize


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())
RARFILE_DATA = \
    b'Rar!\x1a\x07\x00\xcf\x90s\x00\x00\r\x00\x00\x00\x00\x00\x00\x00l\x18t ' \
    b'\x80)\x00\x17\x00\x00\x00\x0c\x00\x00\x00\x03-;\x08\xaf/\x83\x8fK' \
    b'\x1d3\t\x00\xb4\x81\x00\x00hello.txt\x08\x0c\xcb\xec\xcfw\x8a{\x85' \
    b'\x07\x08\x14\x1co\xfb\x7f\xfd\xbbA[^eD\xc4={\x00@\x07\x00'


class Backend(BaseBackend):

    @staticmethod
    @memoize
    def check(title):
        # If "unrar" sysdep is not installed this will fail.
        with ExitStack() as stack:
            tfile = stack.enter_context(
                tempfile.NamedTemporaryFile(suffix='.rar'))
            tfile.write(RARFILE_DATA)
            tfile.flush()
            tfile.seek(0)

            archive = stack.enter_context(rarfile.RarFile(tfile))
            for f in archive.infolist():
                rf = stack.enter_context(archive.open(f))
                rf.read()

    def handle_fobj(self, f):
        with ExitStack() as stack:
            text = StringIO()
            archive = stack.enter_context(rarfile.RarFile(f))
            for f in archive.infolist():
                LOGGER.debug("extracting %s" % f.filename)

                rf = stack.enter_context(archive.open(f))
                ret = get(rf, name=f.filename, encoding=self.encoding,
                          encoding_errors=self.encoding_errors)
                text.write(ret)

            return text.getvalue()

    handle_path = handle_fobj
