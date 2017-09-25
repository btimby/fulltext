from __future__ import absolute_import

from fulltext.util import run


EXTENSIONS = ('doc', )


def _get_file(f, **kwargs):
    return run('antiword', '-', stdin=f).decode('utf8')


def _get_path(path, **kwargs):
    return run('antiword', path).decode('utf8')
