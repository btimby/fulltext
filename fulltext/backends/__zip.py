from __future__ import absolute_import

import zipfile

from six import StringIO
from contextlib2 import ExitStack

from fulltext import get


def _get_file(f, **kwargs):
    with ExitStack() as stack:
        text = StringIO()
        z = stack.enter_context(zipfile.ZipFile(f, 'r'))
        for name in sorted(z.namelist()):
            zf = stack.enter_context(z.open(name, 'r'))
            # Kinda hacky, but zipfile's open() does not handle "b" in
            # the mode.
            # We do this here to satisy an assertion in _get_file().
            zf.mode += 'b'
            text.write(get(zf, name=name))

        return text.getvalue()


_get_path = _get_file
