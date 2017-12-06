from __future__ import absolute_import

import re
import logging
import os
import shutil
import tempfile
import mimetypes
import sys

from os.path import splitext

from six import string_types
from six import PY3
from fulltext.util import warn
from fulltext.util import magic


__all__ = ["get", "register_backend"]


# --- overridable defaults

ENCODING = sys.getfilesystemencoding()
ENCODING_ERRORS = "strict"
TEMPDIR = os.environ.get('FULLTEXT_TEMP', tempfile.gettempdir())
DEFAULT_MIME = 'application/octet-stream'

# --- others

LOGGER = logging.getLogger(__file__)
LOGGER.addHandler(logging.NullHandler())
STRIP_WHITE = re.compile(r'[ \t\v\f\r\n]+')
SENTINAL = object()
MIMETYPE_TO_BACKENDS = {}
EXTS_TO_MIMETYPES = {}
MAGIC_BUFFER_SIZE = 1024

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
        assert ext, ext
        EXTS_TO_MIMETYPES[ext] = mimetype
    else:
        if not isinstance(extensions, (list, tuple, set, frozenset)):
            raise TypeError("invalid extensions type (got %r)" % extensions)
        for ext in set(extensions):
            ext = ext if ext.startswith('.') else '.' + ext
            assert ext, ext
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

for mt in ('text/html', 'application/html', 'text/xhtml'):
    register_backend(
        mt,
        'fulltext.backends.__html',
        extensions=['.htm', '.html', '.xhtml'])

register_backend(
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'fulltext.backends.__docx')

register_backend(
    'application/msword',
    'fulltext.backends.__doc',
    extensions=['.doc'])

for mt in ('text/csv', 'text/tsv', 'text/psv'):
    register_backend(
        mt,
        'fulltext.backends.__csv',
        extensions=['.csv', '.tsv', '.psv', '.tab'])

for mt in ("application/epub", "application/epub+zip"):
    register_backend(
        mt,
        'fulltext.backends.__epub',
        extensions=[".epub"])

register_backend(
    'application/postscript',
    'fulltext.backends.__ps',
    extensions=[".ps", ".eps", ".ai"])

register_backend(
    'message/rfc822',
    'fulltext.backends.__eml',
    extensions=['.eml'])

register_backend(
    'application/mbox',
    'fulltext.backends.__mbox',
    extensions=['.mbox'])

register_backend(
    'application/vnd.ms-outlook',
    'fulltext.backends.__msg',
    extensions=['.msg'])

register_backend(
    'application/gzip',
    'fulltext.backends.__gz',
    extensions=['.gz'])

register_backend(
    'application/json',
    'fulltext.backends.__json',
    extensions=['.json'])

# default backend.
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
    try:
        if 'b' in getattr(f, 'mode', ''):
            return True
    except TypeError:
        import gzip
        if isinstance(f, gzip.GzipFile):
            return True  # in gzip mode is an integer
        raise

    # Can we sniff?
    try:
        f.seek(0, os.SEEK_CUR)
    except (AttributeError, IOError):
        return False

    # Finally, let's sniff by reading a byte.
    byte = f.read(1)
    f.seek(-1, os.SEEK_CUR)
    return hasattr(byte, 'decode')


def is_file_path(obj):
    """Return True if obj is a possible file path or name."""
    return isinstance(obj, string_types) or isinstance(obj, bytes)


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

    else:
        raise AssertionError(
            'Backend %s has no _get functions' % backend.__name__)


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

        with tempfile.NamedTemporaryFile(dir=TEMPDIR, suffix=ext) as t:
            shutil.copyfileobj(f, t)
            t.flush()
            return backend._get_path(t.name, **kwargs)

    else:
        raise AssertionError(
            'Backend %s has no _get functions' % backend.__name__)


def backend_from_mime(mime):
    """Determine backend module object from a mime string."""
    try:
        mod_name = MIMETYPE_TO_BACKENDS[mime]
    except KeyError:
        warn("don't know how to handle %r mime; assume %r" % (
            mime, DEFAULT_MIME))
        mod_name = MIMETYPE_TO_BACKENDS[DEFAULT_MIME]
    mod = __import__(mod_name, fromlist=[' '])
    return mod


def backend_from_fname(name):
    """Determine backend module object from a file name."""
    ext = splitext(name)[1]
    try:
        mime = EXTS_TO_MIMETYPES[ext]
    except KeyError:
        with open(name, 'rb') as f:
            return backend_from_fobj(f)
    else:
        mod_name = MIMETYPE_TO_BACKENDS[mime]
        mod = __import__(mod_name, fromlist=[' '])
        return mod


def backend_from_fobj(f):
    """Determine backend module object from a file object."""
    if magic is None:
        warn("magic lib is not installed; assuming mime type %r" % (
            DEFAULT_MIME))
        return backend_from_mime(DEFAULT_MIME)
    else:
        offset = f.tell()
        try:
            f.seek(0)
            chunk = f.read(MAGIC_BUFFER_SIZE)
            mime = magic.from_buffer(chunk, mime=True)
            return backend_from_mime(mime)
        finally:
            f.seek(offset)


def _get(path_or_file, default, mime, name, backend, encoding,
         encoding_errors, kwargs):
    # Find backend module.
    if backend is None:
        if mime:
            backend_mod = backend_from_mime(mime)
        elif name:
            backend_mod = backend_from_fname(name)
        else:
            if is_file_path(path_or_file):
                backend_mod = backend_from_fname(path_or_file)
            else:
                if hasattr(path_or_file, "name"):
                    backend_mod = backend_from_fname(path_or_file.name)
                else:
                    backend_mod = backend_from_fobj(path_or_file)
    else:
        if isinstance(backend, string_types):
            try:
                mime = EXTS_TO_MIMETYPES['.' + backend]
            except KeyError:
                raise ValueError("invalid backend %r" % backend)
            backend_mod = backend_from_mime(mime)
        else:
            backend_mod = backend

    # Call backend.
    fun = _get_path if is_file_path(path_or_file) else _get_file
    text = fun(backend_mod, path_or_file, **kwargs)
    assert text is not None, "backend function returned None"
    text = STRIP_WHITE.sub(' ', text)
    return text.strip()


def get(path_or_file, default=SENTINAL, mime=None, name=None, backend=None,
        encoding=None, encoding_errors=None, kwargs=None):
    """
    Get document full text.

    Accepts a path or file-like object.
     * If given, `default` is returned instead of an error.
     * `backend` is either a module object or a string specifying which
       default backend to use (e.g. "doc"); take a look at backends
       directory to see a list of default backends.
     * `mime` and `name` should be passed if the information
       is available to caller, otherwise a best guess is made.
       If both are specified `mime` takes precedence.
     * `encoding` and `encoding_errors` are used to handle text encoding.
       They are taken into consideration mostly only by pure-python
       backends which do not rely on CLI tools.
       Default to "utf8" and "strict" respectively.
     * `kwargs` are passed to the underlying backend.
    """
    if encoding is None:
        encoding = ENCODING
    if encoding_errors is None:
        encoding_errors = ENCODING_ERRORS

    kwargs = kwargs or {}
    kwargs.setdefault("mime", mime)
    kwargs.setdefault("encoding", encoding)
    kwargs.setdefault("encoding_errors", encoding_errors)

    try:
        return _get(path_or_file, default=default, mime=mime, name=name,
                    backend=backend, kwargs=kwargs, encoding=encoding,
                    encoding_errors=encoding_errors)
    except Exception as e:
        if default is not SENTINAL:
            LOGGER.exception(e)
            return default
        raise
