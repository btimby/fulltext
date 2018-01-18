from __future__ import absolute_import

import errno
import re
import logging
import os
import mimetypes
import sys

from os.path import splitext

from six import string_types
from six import PY3
from fulltext.util import warn
from fulltext.util import magic
from fulltext.util import is_file_path
from fulltext.util import fobj_to_tempfile
from fulltext.util import is_windows

__all__ = ["get", "register_backend"]


# --- overridable defaults

ENCODING = sys.getfilesystemencoding()
ENCODING_ERRORS = "strict"
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

# A list of extensions which will be treated as pure text.
# This takes precedence over register_backend().
# https://www.openoffice.org/dev_docs/source/file_extensions.html
_TEXT_EXTS = set((
    ".asm",  # Non-UNIX assembler source file
    ".asp",  # Active Server Page
    ".awk",  # An awk script file
    ".bat",  # MS-DOS batch file
    ".c",    # C language file
    ".class",  # Compiled java source code file
    ".cmd",  # Compiler command file
    ".cpp",  # C++ language file
    ".cxx",  # C++ language file
    ".def",  # Win32 library definition file
    ".dpc",  # Source dependency file containing list of dependencies
    ".dpj",  # Java source dependency file containing list of dependencies
    ".h",    # C header file
    ".hpp",  # Generated C++ header or header plus plus file
    ".hrc",  # An ".src",  # include header file
    ".hxx",  # C++ header file
    ".in",
    ".inc",  # Include file
    ".ini",  # Initialization file
    ".inl",  # Inline header file
    ".jar",  # Java classes archive file
    ".java",  # Java language file
    ".js",   # JavaScript code file
    ".jsp",  # Java Server Page file
    ".kdelnk",  # KDE1 configuration file
    ".l",    # Lex source code file
    ".ll",   # Lex source code file
    ".lnx",  # Linux-specific makefile
    ".log",  # Log file
    ".lst",  # ASCII database file used in solenv
    ".MacOS",
    ".md",   # Markdown language.
    ".mk",   # A dmake makefile
    ".mod",  # BASIC module file
    ".par",  # Script particles file
    ".pl",   # Perl script
    ".plc",  # Former build script file, now obsolete
    ".pld",  # Former build script file, now obsolete
    ".pm",   # Perl module file
    ".pmk",  # Project makefiles
    ".pre",  # Preprocessor output from scpcomp
    ".py",   # Python
    ".pyx",  # Cython
    ".r",    # Resource file for Macintosh
    ".rc",   # A dmake recursive makefile or a Win32 resource script file
    ".rdb",  # Interface and type description database (type library)
    ".res",  # Resource file
    ".rst",  # Restructured text
    ".s",    # Assembler source file (UNIX)
    ".sbl",  # BASIC file
    ".scp",  # Script source file
    ".sh",   # Shell script
    ".src",  # Source resource string file
    ".txt",  # Language text file
    ".y",    # Yacc source code file
    ".yaml",  # Yaml
    ".yml",  # Yaml
    ".yxx",  # Bison source code file
))


# XXX: dirty hack for pyinstaller so that it includes these modules.
# TODO: find a way to do this in pyinstaller.spec instead.
if is_windows() and hasattr(sys, '_MEIPASS'):
    from fulltext.backends import __bin  # NOQA
    from fulltext.backends import __csv  # NOQA
    from fulltext.backends import __doc  # NOQA
    from fulltext.backends import __docx  # NOQA
    from fulltext.backends import __eml  # NOQA
    from fulltext.backends import __epub  # NOQA
    from fulltext.backends import __gz  # NOQA
    from fulltext.backends import __html  # NOQA
    from fulltext.backends import __hwp  # NOQA
    from fulltext.backends import __json  # NOQA
    from fulltext.backends import __mbox  # NOQA
    # XXX couldn't find a way to install ExtractMessage lib with
    # pyinstaller.
    # from fulltext.backends import __msg  # NOQA
    from fulltext.backends import __ocr  # NOQA
    from fulltext.backends import __odt  # NOQA
    from fulltext.backends import __pdf  # NOQA
    from fulltext.backends import __pptx  # NOQA
    from fulltext.backends import __ps  # NOQA
    from fulltext.backends import __rar  # NOQA
    from fulltext.backends import __rtf  # NOQA
    from fulltext.backends import __text  # NOQA
    from fulltext.backends import __xlsx  # NOQA
    from fulltext.backends import __xml  # NOQA
    from fulltext.backends import __zip  # NOQA


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
    'fulltext.backends.__zip',
    extensions=[".zip"])

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
    'fulltext.backends.__xlsx',
    extensions=['.xlsx'])

register_backend(
    'text/plain',
    'fulltext.backends.__text',
    extensions=['.txt', '.text'])

register_backend(
    'application/rtf',
    'fulltext.backends.__rtf',
    extensions=['.rtf'])

register_backend(
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # NOQA
    'fulltext.backends.__pptx',
    extensions=['.pptx'])

register_backend(
    'application/pdf',
    'fulltext.backends.__pdf',
    extensions=['.pdf'])

register_backend(
    'application/vnd.oasis.opendocument.text',
    'fulltext.backends.__odt',
    extensions=['.odt'])

register_backend(
    'application/vnd.oasis.opendocument.spreadsheet',
    'fulltext.backends.__odt',
    extensions=['.ods'])

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
    'fulltext.backends.__ocr',
    extensions=['.png'])

register_backend(
    'image/gif',
    'fulltext.backends.__ocr',
    extensions=['.gif'])

register_backend(
    'application/x-hwp',
    'fulltext.backends.__hwp',
    extensions=['.hwp'])

for mt in ('text/html', 'application/html', 'text/xhtml'):
    register_backend(
        mt,
        'fulltext.backends.__html',
        extensions=['.htm', '.html', '.xhtml'])

register_backend(
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'fulltext.backends.__docx',
    extensions=['.docx'])

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

# Extensions which will be treated as pure text.
# We just come up with a custom mime name.
for ext in _TEXT_EXTS:
    register_backend(
        '[custom-fulltext-mime]/%s' % ext,
        'fulltext.backends.__text',
        extensions=[ext])


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
        LOGGER.warning(
            "Using disk, %r backend does not provide `handle_fobj()`", backend)

        ext = ''
        if 'ext' in kwargs:
            ext = '.' + kwargs['ext']

        with fobj_to_tempfile(f, suffix=ext) as fname:
            return backend.handle_path(fname, **kwargs)
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
        msg = "No handler for %r, defaulting to %r" % (mime, DEFAULT_MIME)
        if 'FULLTEXT_TESTING' in os.environ:
            warn(msg)
        else:
            LOGGER.debug(msg)

        mod_name = MIMETYPE_TO_BACKENDS[DEFAULT_MIME]
    mod = import_mod(mod_name)
    return mod


def backend_from_fname(name):
    """Determine backend module object from a file name."""
    ext = splitext(name)[1]

    try:
        mime = EXTS_TO_MIMETYPES[ext]

    except KeyError:
        try:
            f = open(name, 'rb')

        except IOError as e:
            # The file may not exist, we are being asked to determine it's type
            # from it's name. Other errors are unexpected.
            if e.errno != errno.ENOENT:
                raise

            # We will have to fall back upon the default backend.
            msg = "No handler for %r, defaulting to %r" % (ext, DEFAULT_MIME)
            if 'FULLTEXT_TESTING' in os.environ:
                warn(msg)
            else:
                LOGGER.debug(msg)

            mod_name = MIMETYPE_TO_BACKENDS[DEFAULT_MIME]

        else:
            with f:
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
