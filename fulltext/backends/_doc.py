from __future__ import absolute_import

from fulltext.util import run


EXTENSIONS = ('doc', )


def _get_file(f, **kwargs):
    return run('antiword', '-', stdin=f)


def _get_path(path, **kwargs):
    return run('antiword', path)
