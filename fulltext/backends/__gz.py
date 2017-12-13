import gzip
from os.path import splitext, basename

from fulltext import get, backend_from_fname, backend_from_fobj
from fulltext import BaseBackend
from fulltext.util import is_file_path
from fulltext.util import fobj_to_tempfile


def orig_fname(s):
    s = basename(s)
    if s.lower().endswith('.gz'):
        s = s[:-3]
    return s


def _has_ext(s):
    return bool(splitext(s)[1])


class Backend(BaseBackend):

    def handle_fobj(self, path_or_file):
        if is_file_path(path_or_file):
            f = gzip.GzipFile(path_or_file)
            path = path_or_file
        else:
            f = gzip.GzipFile(fileobj=path_or_file)
            path = f.name

        with f:
            orig_name = orig_fname(path)
            if _has_ext(orig_name) and splitext(orig_name)[1].lower() != '.gz':
                backend = backend_from_fname(orig_name)
            else:
                backend = backend_from_fobj(f)
            # This sucks but apparently some backends are not able to
            # deal with gzip.GzipFile instances so we copy the file on
            # disk. See: https://github.com/btimby/fulltext/issues/56
            with fobj_to_tempfile(f, suffix=splitext(orig_name)[1]) as fname:
                return get(fname, backend=backend)

    handle_path = handle_fobj
