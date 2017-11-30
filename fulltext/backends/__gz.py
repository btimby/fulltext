import gzip
from os.path import splitext, basename

from fulltext import get, backend_from_fname, backend_from_fobj, is_file_path


def _orig_fname(s):
    s = basename(s)
    if s.lower().endswith('.gz'):
        s = s[:-3]
    return s


def _has_ext(s):
    return bool(splitext(s)[1])


def _get_file(path_or_file, **kwargs):
    if is_file_path(path_or_file):
        f = gzip.GzipFile(path_or_file)
        path = path_or_file
    else:
        f = gzip.GzipFile(fileobj=path_or_file)
        path = f.name

    with f:
        orig_name = _orig_fname(path)
        if _has_ext(orig_name) and splitext(orig_name)[1].lower() != '.gz':
            backend = backend_from_fname(orig_name)
        else:
            backend = backend_from_fobj(f)
        return get(f, backend=backend)
