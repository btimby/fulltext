from __future__ import absolute_import
from fulltext.util import BaseBackend
from fulltext.util import warn


class Backend(BaseBackend):
    def handle_path(self, path):
        warn('this file is not supported: %r' % path)
        return ''

    def handle_fobj(self, f):
        name = getattr(f, 'name', None)
        if name:
            warn('this file is not supported: %r' % name)
        else:
            warn('unsupported file was given')
        return ''
