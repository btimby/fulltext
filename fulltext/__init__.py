from __future__ import absolute_import

import re
import logging
import os
import shutil
import tempfile
import mimetypes

from os.path import splitext

from six import string_types
from six import PY3
from fulltext.util import warn


__all__ = ["get", "register_backend"]


LOGGER = logging.getLogger(__file__)
LOGGER.addHandler(logging.NullHandler())

FULLTEXT_TEMP = os.environ.get('FULLTEXT_TEMP', tempfile.gettempdir())
FULLTEXT_PATH = os.environ.get('FULLTEXT_PATH', '')

STRIP_WHITE = re.compile(r'[ \t\v\f]+')
STRIP_EOL = re.compile(r'[\r\n]+')
SENTINAL = object()
BACKENDS = {}
MIMETYPE_TO_BACKENDS = {}
EXTS_TO_MIMETYPES = {}

mimetypes.init()
_MIMETYPES_TO_EXT = dict([(v, k) for k, v in mimetypes.types_map.items()])


def register_backend(mimetype, module, extensions=None):
    """Register a backend.
    `mimetype`: a mimetype string (e.g. 'text/plain')
    `module`: an import string (e.g. path.to.my.module)
    `extensions`: a list of extensions (e.g. ['txt', 'text'])
    """
    if mimetype in MIMETYPE_TO_BACKENDS:
        warn("overwriting %r mimetype which was already set" % mimetype)
    MIMETYPE_TO_BACKENDS[mimetype] = module
    if extensions is None:
        try:
            ext = _MIMETYPES_TO_EXT[mimetype]
        except KeyError:
            raise KeyError(
                "mimetypes module has no extension associated "
                "with %r mimetype; use 'extensions' arg yourself" % mimetype)
        EXTS_TO_MIMETYPES[ext] = mimetype
    else:
        if not isinstance(extensions, (list, tuple, set, frozenset)):
            raise TypeError("invalid extensions type (got %r)" % extensions)
        for ext in set(extensions):
            ext = ext if ext.startswith('.') else '.' + ext
            EXTS_TO_MIMETYPES[ext] = mimetype


register_backend(
    'application/zip',
    'fulltext.backends.__zip')

for mt in ("text/xml", "application/xml", "application/x-xml"):
    register_backend(
        mt,
        'fulltext.backends.__xml',
        extensions=[".xml", ".xsd"])

register_backend(
    'application/vnd.ms-excel',
    'fulltext.backends.__xlsx',
    extensions=['.xls', '.xlsx'])

register_backend(
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'fulltext.backends.__xlsx')

register_backend(
    'text/plain',
    'fulltext.backends.__text',
    extensions=['.txt', '.text'])

register_backend(
    'application/rtf',
    'fulltext.backends.__rtf')

register_backend(
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # NOQA
    'fulltext.backends.__pptx')

register_backend(
    'application/pdf',
    'fulltext.backends.__pdf')

register_backend(
    'application/vnd.oasis.opendocument.text',
    'fulltext.backends.__odt')

register_backend(
    'application/vnd.oasis.opendocument.spreadsheet',
    'fulltext.backends.__odt')

# images
register_backend(
    'image/jpeg',
    'fulltext.backends.__ocr',
    extensions=['.jpg', '.jpeg'])
register_backend(
    'image/bmp',
    'fulltext.backends.__ocr',
    extensions=['.bmp'])
register_backend(
    'image/png',
    'fulltext.backends.__ocr')
register_backend(
    'image/gif',
    'fulltext.backends.__ocr')

register_backend(
    'application/x-hwp',
    'fulltext.backends.__hwp')

register_backend(
    'text/html',
    'fulltext.backends.__html',
    extensions=['.htm', '.html'])

register_backend(
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'fulltext.backends.__docx')

register_backend(
    'application/msword',
    'fulltext.backends.__doc',
    extensions=['.doc'])

register_backend(
    'text/csv',
    'fulltext.backends.__csv')

register_backend(
    'application/octet-stream',
    'fulltext.backends.__bin',
    extensions=['.a', '.bin'])


def is_binary(f):
    """Return True if binary mode."""
    # NOTE: order matters here. We don't bail on Python 2 just yet. Both
    # codecs.open() and io.open() can open in text mode, both set the encoding
    # attribute. We must do that check first.

    # If it has a decoding attribute with a value, it is text mode.
    if getattr(f, "encoding", None):
        return False

    # Python 2 makes no further distinction.
    if not PY3:
        return True

    # If the file has a mode, and it contains b, it is binary.
    if 'b' in getattr(f, 'mode', ''):
        return True

    # Can we sniff?
    try:
        f.seek(0, os.SEEK_CUR)
    except (AttributeError, IOError):
        return False

    # Finally, let's sniff by reading a byte.
    byte = f.read(1)
    f.seek(-1, os.SEEK_CUR)
    return hasattr(byte, 'decode')


def _get_path(backend, path, **kwargs):
    """
    Handle a path.

    Called by `get()` when provided a path. This function will prefer the
    backend's `_get_path()` if one is provided Otherwise, it will open the
    given path then use `_get_file()`.
    """
    if callable(getattr(backend, '_get_path', None)):
        # Prefer _get_path() if present.
        return backend._get_path(path, **kwargs)

    elif callable(getattr(backend, '_get_file', None)):
        # Fallback to _get_file(). No warning here since the performance hit
        # is minimal.
        with open(path, 'rb') as f:
            return backend._get_file(f, **kwargs)


def _get_file(backend, f, **kwargs):
    """
    Handle a file-like object.

    Called by `get()` when provided a file-like. This function will prefer the
    backend's `_get_file()` if one is provided. Otherwise, it will write the
    data to a temporary file and call `_get_path()`.
    """
    if not is_binary(f):
        raise AssertionError('File must be opened in binary mode.')

    if callable(getattr(backend, '_get_file', None)):
        # Prefer _get_file() if present.
        return backend._get_file(f, **kwargs)

    elif callable(getattr(backend, '_get_path', None)):
        # Fallback to _get_path(). Warn user since this is potentially
        # expensive.
        LOGGER.warning("Using disk, backend does not provide `_get_file()`")

        ext = ''
        if 'ext' in kwargs:
            ext = '.' + kwargs['ext']

        with tempfile.NamedTemporaryFile(dir=FULLTEXT_TEMP, suffix=ext) as t:
            shutil.copyfileobj(f, t)
            t.flush()
            return backend._get_path(t.name, **kwargs)


def backend_from_mime(mime):
    mod_name = MIMETYPE_TO_BACKENDS
    mod = __import__(mod_name, fromlist=[' '])
    return mod


def backend_from_ext(ext):
    if not ext.startswith('.'):
        ext = "." + ext
    try:
        mime = EXTS_TO_MIMETYPES[ext]
    except KeyError:
        warn("don't know how to handle %r extension; assume binary" % ext)
        mime = 'application/octet-stream'
    mod_name = MIMETYPE_TO_BACKENDS[mime]
    mod = __import__(mod_name, fromlist=[' '])
    return mod


def get(path_or_file, default=SENTINAL, mime=None, name=None, backend=None,
        kwargs={}):
    """
    Get document full text.

    Accepts a path or file-like object.
     * If given, `default` is returned instead of an error.
     * `backend` is a string specifying which default backend to use
       (e.g. "doc"); take a look at backends directory to see a list of
       default backends.
     * `mime` and `name` should be passed if the information
       is available to caller, otherwise a best guess is made.
       If both are specified `mime` takes precedence.
     * `kwargs` are passed to the underlying backend.
    """
    # Find backend.
    if backend is None:
        if mime:
            raise NotImplementedError  # TODO
        elif name:
            backend_mod = backend_from_ext(splitext(name)[1])
        else:
            if isinstance(path_or_file, string_types):
                backend_mod = backend_from_ext(splitext(path_or_file)[1])
            else:
                raise NotImplementedError  # TODO
    else:
        backend_mod = backend_from_ext(backend)

    # Call backend.
    fun = _get_path if isinstance(path_or_file, string_types) else _get_file
    kwargs.setdefault("mime", mime)
    try:
        text = fun(backend_mod, path_or_file, **kwargs)

    except Exception as e:
        LOGGER.exception(e)
        if default is not SENTINAL:
            return default
        raise

    else:
        text = STRIP_WHITE.sub(' ', text)
        text = STRIP_EOL.sub(' ', text)
        return text.strip()
