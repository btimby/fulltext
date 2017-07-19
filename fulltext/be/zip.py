from __future__ import absolute_import

import zipfile

from fulltext import get

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO


def _get_file(f, **kwargs):
    text, z = StringIO(), zipfile.ZipFile(f, 'r')
    for name in sorted(z.namelist()):
        text.write(get(z.open(name, 'r'), name=name))
    return text.getvalue()

def _get_path(path, **kwargs):
    return _get_file(path, **kwargs)
