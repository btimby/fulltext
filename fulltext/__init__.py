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
from fulltext.util import is_file_path


__all__ = ["get", "register_backend"]


# --- overridable defaults

ENCODING = sys.getfilesystemencoding()
ENCODING_ERRORS = "strict"
TEMPDIR = os.environ.get('FULLTEXT_TEMP', tempfile.gettempdir())
DEFAULT_MIME = 'application/octet-stream'

# --- others

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())
STRIP_WHITE = re.compile(r'[ \t\v\f\r\n]+')
SENTINAL = object()
MIMETYPE_TO_BACKENDS = {}
EXTS_TO_MIMETYPES = {}
MAGIC_BUFFER_SIZE = 1024

mimetypes.init()
_MIMETYPES_TO_EXT = dict([(v, k) for k, v in mimetypes.types_map.items()])


# =====================================================================
# --- backends
# =====================================================================

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

register_backend(
    'application/x-rar-compressed',
    'fulltext.backends.__rar',
    extensions=['.rar'])

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


# =====================================================================
# --- utils
# =====================================================================


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


def handle_path(backend_inst, path, **kwargs):
    """
    Handle a path.

    Called by `get()` when provided a path. This function will prefer the
    backend's `handle_path()` if one is provided Otherwise, it will open the
    given path then use `handle_fobj()`.
    """
    if callable(getattr(backend_inst, 'handle_path', None)):
        # Prefer handle_path() if present.
        LOGGER.debug("using handle_path")
        return backend_inst.handle_path(path)

    elif callable(getattr(backend_inst, 'handle_fobj', None)):
        # Fallback to handle_fobj(). No warning here since the performance hit
        # is minimal.
        LOGGER.debug("using handle_fobj")
        with open(path, 'rb') as f:
            return backend_inst.handle_fobj(f)

    else:
        raise AssertionError(
            'Backend %s has no _get functions' % backend_inst.__name__)


def handle_fobj(backend, f, **kwargs):
    """
    Handle a file-like object.

    Called by `get()` when provided a file-like. This function will prefer the
    backend's `handle_fobj()` if one is provided. Otherwise, it will write the
    data to a temporary file and call `handle_path()`.
    """
    if not is_binary(f):
        raise AssertionError('File must be opened in binary mode.')

    if callable(getattr(backend, 'handle_fobj', None)):
        # Prefer handle_fobj() if present.
        LOGGER.debug("using handle_fobj")
        return backend.handle_fobj(f)

    elif callable(getattr(backend, 'handle_path', None)):
        # Fallback to handle_path(). Warn user since this is potentially
        # expensive.
        LOGGER.debug("using handle_path")
        LOGGER.warning("Using disk, backend does not provide `handle_fobj()`")

        ext = ''
        if 'ext' in kwargs:
            ext = '.' + kwargs['ext']

        with tempfile.NamedTemporaryFile(dir=TEMPDIR, suffix=ext) as t:
            shutil.copyfileobj(f, t)
            t.flush()
            return backend.handle_path(t.name, **kwargs)

    else:
        raise AssertionError(
            'Backend %s has no _get functions' % backend.__name__)


def import_mod(mod_name):
    return __import__(mod_name, fromlist=[' '])


def backend_from_mime(mime):
    """Determine backend module object from a mime string."""
    try:
        mod_name = MIMETYPE_TO_BACKENDS[mime]
    except KeyError:
        warn("don't know how to handle %r mime; assume %r" % (
            mime, DEFAULT_MIME))
        mod_name = MIMETYPE_TO_BACKENDS[DEFAULT_MIME]
    mod = import_mod(mod_name)
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
        mod = import_mod(mod_name)
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


def backend_inst_from_mod(mod, encoding, encoding_errors, kwargs):
    """Given a mod and a set of opts return an instantiated
    Backend class.
    """
    kw = dict(encoding=encoding, encoding_errors=encoding_errors,
              kwargs=kwargs)
    try:
        klass = getattr(mod, "Backend")
    except AttributeError:
        raise AttributeError("%r mod does not define any backend class" % mod)
    inst = klass(**kw)
    try:
        inst.check(title=False)
    except Exception as err:
        bin_mod = "fulltext.backends.__bin"
        warn("can't use %r due to %r; use %r backend instead" % (
             mod, str(err), bin_mod))
        inst = import_mod(bin_mod).Backend(**kw)
        inst.check(title=False)
    LOGGER.debug("using %r" % inst)
    return inst


# =====================================================================
# --- public API
# =====================================================================


class BaseBackend(object):
    """Base class for defining custom backend classes."""

    def __init__(self, encoding, encoding_errors, kwargs):
        """These are the same args passed to get() function."""
        self.encoding = encoding
        self.encoding_errors = encoding_errors
        self.kwargs = kwargs

    def setup(self):
        """May be overridden by subclass. This is called before handle_
        methods.
        """
        pass

    def teardown(self):
        """May be overridden by subclass. This is called after text
        is extracted, also in case of exception.
        """
        pass

    def check(self, title):
        """May be overridden by subclass. This is called before text
        extraction. If the overriding method raises an exception
        a warning is printed and bin backend is used.
        """
        pass

    def decode(self, s):
        """Decode string."""
        return s.decode(self.encoding, self.encoding_errors)

    def handle_title(self, path_or_file):
        """May be overridden by sublass in order to retrieve file title."""
        return None


def _get(path_or_file, default, mime, name, backend, encoding,
         encoding_errors, kwargs, _wtitle):
    if encoding is None:
        encoding = ENCODING
    if encoding_errors is None:
        encoding_errors = ENCODING_ERRORS

    kwargs = kwargs.copy() if kwargs is not None else {}
    kwargs.setdefault("mime", mime)

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

    # Get backend class.
    inst = backend_inst_from_mod(
        backend_mod, encoding, encoding_errors, kwargs)
    fun = handle_path if is_file_path(path_or_file) else handle_fobj

    # Run handle_ function, handle callbacks.
    title = None
    inst.setup()
    try:
        text = fun(inst, path_or_file)
        if _wtitle:
            try:
                title = inst.handle_title(path_or_file)
            except Exception:
                LOGGER.exception("error while getting title (setting to None)")
    finally:
        inst.teardown()

    assert text is not None, "backend function returned None"
    text = STRIP_WHITE.sub(' ', text)
    text = text.strip()
    return (text, title)


def get(path_or_file, default=SENTINAL, mime=None, name=None, backend=None,
        encoding=None, encoding_errors=None, kwargs=None,
        _wtitle=False):
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
    try:
        text, title = _get(
            path_or_file, default=default, mime=mime, name=name,
            backend=backend, kwargs=kwargs, encoding=encoding,
            encoding_errors=encoding_errors, _wtitle=_wtitle)
        if _wtitle:
            return (text, title)
        else:
            return text
    except Exception as e:
        if default is not SENTINAL:
            LOGGER.exception(e)
            return default
        raise


def get_with_title(*args, **kwargs):
    """Like get() but also tries to determine document title.
    Returns a (text, title) tuple.
    """
    kwargs['_wtitle'] = True
    return get(*args, **kwargs)
