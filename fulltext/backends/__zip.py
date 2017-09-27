from __future__ import absolute_import

import zipfile

from six import StringIO

from fulltext import get


EXTENSIONS = ('zip', )


def _get_file(f, **kwargs):
    text, z = StringIO(), zipfile.ZipFile(f, 'r')
    for name in sorted(z.namelist()):
        text.write(get(z.open(name, 'r'), name=name))
    return text.getvalue()

_get_path = _get_file
