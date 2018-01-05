from __future__ import absolute_import

import logging
import zipfile

from six import StringIO
from contextlib2 import ExitStack

from fulltext.util import BaseBackend, get


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class Backend(BaseBackend):

    def handle_fobj(self, f):
        with ExitStack() as stack:
            text = StringIO()
            z = stack.enter_context(zipfile.ZipFile(f, 'r'))
            for name in sorted(z.namelist()):
                LOGGER.debug("extracting %s" % name)
                zf = stack.enter_context(z.open(name, 'r'))
                # Kinda hacky, but zipfile's open() does not handle "b" in
                # the mode.
                # We do this here to satisy an assertion in handle_fobj().
                zf.mode += 'b'
                text.write(get(zf, name=name))

            return text.getvalue()

    handle_path = handle_fobj
