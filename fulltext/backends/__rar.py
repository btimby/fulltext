from __future__ import absolute_import
import logging

import rarfile
from six import StringIO
from contextlib2 import ExitStack

from fulltext import BaseBackend, get


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class Backend(BaseBackend):

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
