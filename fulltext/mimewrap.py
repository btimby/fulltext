"""
Mime types machinery.
"""

import mimetypes
from fulltext.util import warn


mimetypes.init()
MIMETYPE_TO_BACKENDS = {}
EXTS_TO_MIMETYPES = {}
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
