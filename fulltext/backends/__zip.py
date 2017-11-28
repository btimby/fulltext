from __future__ import absolute_import

import zipfile

from six import StringIO

from fulltext import get


EXTENSIONS = ('zip', )


def _get_file(f, **kwargs):
    text, z = StringIO(), zipfile.ZipFile(f, 'r')
    for name in sorted(z.namelist()):
        zf = z.open(name, 'r')

        # Kinda hacky, but zipfile's open() does not handle "b" in the mode.
        # We do this here to satisy an assertion in _get_file().
        zf.mode += 'b'

        try:
            text.write(get(zf, name=name))
        finally:
            zf.close()

    return text.getvalue()


_get_path = _get_file
