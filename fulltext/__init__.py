import os
import re
import csv
import os.path
import tempfile
import mimetypes
import subprocess


# TODO: Sometimes multiple tools can be used, choose the one that is installed.

mimetypes.add_type('application/rar', '.rar')


STRIP_WHITE = re.compile(r'[ \t\v\f\r\n]+')
UNRTF = re.compile(r'.*-+\n', flags=re.MULTILINE)
DEVNULL = os.open(os.devnull, os.O_RDWR)


class FullTextException(Exception):
    pass


class MissingCommandException(FullTextException):
    def __init__(self, command):
        super(MissingCommandException, self).__init__(
            'Missing command "{0}"'.format(command))


# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program):
    "Simply checks if a given program exists within PATH and is executable."
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None


def read_content(f, type):
    "A handler that simply reads a file's output. Used on unrecognized types."
    if isinstance(f, basestring):
        f = file(f, 'r')
    return f.read()


def run_command(f, type):
    "The default handler. It runs a command and reads it's output."
    cmds = PROG_MAP[type]
    if isinstance(f, basestring):
        cmd = cmds[0]
        cmd = map(lambda x: x.format(f), cmd)
        i = None
    else:
        assert hasattr(f, 'read'), 'File-like object must have read() method.'
        cmd = cmds[1]
        if cmd is None:
            # Use temp file:
            fd, fname = tempfile.mkstemp()
            os.write(fd, f.read())
            os.close(fd)
            return run_command(fname, type)
        i = f.read()
    if which(cmd[0]) is None:
        raise MissingCommandException(cmd[0])
    # We use regular subprocess module here. No timeout is allowed with communicate()
    # If there are problems with timeouts, I will investigate other options, like:
    # http://pypi.python.org/pypi/EasyProcess
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=DEVNULL)
    return p.communicate(i)[0]


def strip_unrtf_header(f, type):
    "Can't find a way to turn off the stupid header in unrtf."
    text = run_command(f, type)
    parts = text.split('-----------------')
    return '-----------------'.join(parts[1:])


def csv_to_text(f, type):
    "Can convert xls to csv, but this will go from csv to plain old text."
    text = run_command(f, type)
    buffer = []
    for row in csv.reader(text.splitlines(), dialect="excel"):
        buffer.append(' '.join(row))
    return ' '.join(buffer)


PROG_MAP = {
    ('application/pdf', None): (
        ('pdftotext', '-q', '-nopgbrk', '{0}', '-'),
        ('pdftotext', '-q', '-nopgbrk', '-', '-'),
    ),
    ('application/msword', None): (
        ('antiword', '{0}'),
        ('antiword', '-'),
    ),
    ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', None): (
        ('docx2txt', '{0}', '-'),  # http://sourceforge.net/projects/docx2txt/
        ('docx2txt', '{0}', '-'),  # http://sourceforge.net/projects/docx2txt/
    ),
    ('application/vnd.ms-excel', None): (
        ('xls2csv', '{0}'),  # as provided by catdoc
        None,  # Supposedly this works, but I get segmentation fault.
    ),
    ('application/rtf', None): (
        ('unrtf', '--text', '--nopict', '{0}'),
        ('unrtf', '--text', '--nopict'),
    ),
    ('application/vnd.oasis.opendocument.text', None): (
        ('odt2txt', '{0}'),
        None,
    ),
    ('application/vnd.oasis.opendocument.spreadsheet', None): (
        ('odt2txt', '{0}'),
        None,
    ),
    ('application/zip', None): (
        ('funzip', '{0}', ),
        ('funzip', ),
    ),
    ('application/x-tar', 'gzip'): (
        ('tar', 'tzf', '{0}'),
        ('tar', 'tz'),
    ),
    ('application/x-tar', 'gzip2'): (
        ('tar', 'tjf', '{0}'),
        ('tar', 'tj'),
    ),
    ('application/rar', None): (
        ('unrar', 'vb', '-p-', '-ierr', '-y', '{0}'),
        None,
    ),
    ('text/html', None): (
        ('html2text', '-nobs', '{0}'),
        ('html2text', '-nobs'),
    ),
    ('text/xml', None): (
        ('html2text', '-nobs', '{0}'),
        ('html2text', '-nobs'),
    ),
    ('image/jpeg', None): (
        ('exiftool', '-s', '-s', '-s', '{0}'),
        ('exiftool', '-s', '-s', '-s', '-'),
    ),
    ('video/mpeg', None): (
        ('exiftool', '-s', '-s', '-s', '{0}'),
        ('exiftool', '-s', '-s', '-s', '-'),
    ),
    ('audio/mpeg', None): (
        ('exiftool', '-s', '-s', '-s', '{0}'),
        ('exiftool', '-s', '-s', '-s', '-'),
    ),
    ('application/octet-stream', None): (
        ('strings', '-n 18', '{0}'),
        ('strings', '-n 18'),
    ),
}
"The command registry. Use add_commands() to override this."

FUNC_MAP = {
    ('application/pdf', None): run_command,
    ('application/msword', None): run_command,
    ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', None): run_command,
    ('application/vnd.ms-excel', None): csv_to_text,
    ('application/rtf', None): strip_unrtf_header,
    ('application/vnd.oasis.opendocument.text', None): run_command,
    ('application/vnd.oasis.opendocument.spreadsheet', None): run_command,
    ('application/zip', None): run_command,
    ('application/x-tar', 'gzip'): run_command,
    ('application/x-tar', 'gzip2'): run_command,
    ('application/rar', None): run_command,
    ('text/html', None): run_command,
    ('text/xml', None): run_command,
    ('image/jpeg', None): run_command,
    ('video/mpeg', None): run_command,
    ('audio/mpeg', None): run_command,
    ('application/octet-stream', None): run_command,
}
"The handler registry. Use add_handler() to override this."


def add_commands(mime, commands, encoding=None):
    """
    Adds a set of commands to the command registry. These commands are used to extract
    text from various file types.

    Each command set consists of two commands. Many of the CLI programs used for
    extraction can be fed data via a file (path) or via stdin. Fulltext accepts both
    paths and file-like objects. In the case of a path, the first command is used by
    simply passing along the path. In the case of a file-like, fulltext will feed it's
    contents to the command via stdin. Some CLI programs do NOT accept data via stdin
    in this case, leave the second command undefined, fulltext will fall back to writing
    the file-like to a temporary file, then invoking the first command on the temp file
    path. This is a basic optimization, that tries to avoid writing to disk when dealing
    with buffers or remote data that does not already reside within the file system.

    Each command is a tuple, which should represent the program name, and any arguments
    needed to cause the program to print plain text to stdout. You need to put `{0}` at
    the location where the input file should reside. string.format() is used to merge in
    the file name being processed when the command is executed.

    Although you would never want to do this, here is how you would register the `cat`
    command for use with plain text files.

    >>> import fulltext
    >>> fulltext.add_commands('text/plain', (('cat', '{0}'), ('cat', )))

    The above is not yet complete, as you still need to register a handler using add_handler().
    """
    assert isinstance(commands, tuple), 'Commands must be tuple (Command for disk file, Command for use with piping).'
    assert len(commands) == 2, 'Commands must contain two commands.'
    assert isinstance(commands[0], tuple), 'First command must be a tuple.'
    assert isinstance(commands[1], tuple) or commands[1] is None, 'Second command must be a tuple or None.'
    PROG_MAP[(mime, encoding)] = commands


def add_handler(mime, handler, encoding=None):
    """
    Adds a function to handle files of a specific type. Most file types use the built-in
    run_command handler. This handler executes a command and reads the output in order
    to convert the file to text. If you use this handler for your file type, then you
    must also use add_commands() to register a command to handle this type.

    Here is how you could register a handler for plain text files.

    >>> import fulltext
    >>> fulltext.add_handler('text/plain', fulltext.run_command)

    As mentioned, this is a contrived example. You would be better served by the following.

    >>> import fulltext
    >>> fulltext.add_handler('text/plain', fulltext.read_content)

    But, since the default action is to read the content of an unrecognized file type,
    registering text/plain is redundant.
    """
    assert callable(handler), 'Handler must be callable.'
    FUNC_MAP[(mime, encoding)] = handler


def add_type(mime, ext):
    """
    Adds a new mime type and associated extension. This just dispatches to the mimetypes
    module for now. It is here only to allow future expansion (if we don't use mimetypes
    forever.)
    """
    assert ext.startswith('.'), 'Extension should start with a period `.`.'
    return mimetypes.add_type(mime, ext)


def add(mime, ext, handler, commands=None, encoding=None):
    """
    Shortcut command to add type, handler and optionally commands. Simply calls add_type(),
    add_handler() and add_commands().
    """
    add_type(mime, ext)
    add_handler(mime, handler, encoding=encoding)
    if commands:
        add_commands(mime, commands, encoding=encoding)


def get_type(filename):
    """
    Gets the mimetype and encoding using the mimetypes module. Defined as a standalone
    function for future expansion.
    """
    return mimetypes.guess_type(filename)


# A placeholder for a kwarg default value.
class NoDefault(object):
    pass


def get(f, default=NoDefault, filename=None, type=None):
    """
    Gets text from a given file. The first parameter can be a path or a file-like object that
    has a read method. Default is a way to supress errors and just return the default text.
    Filename can help figure out the type of file being used if you passed in a file-like
    object. Type can be used to override the type guessing. Type should be a tuple: (mimetype, encoding)
    as returned by the mimetypes library.

    For any recognizable type, a command will be execute to extract the text. Then that text
    will be post processed to remove redundant whitespace.

    For zip files, the first member is extracted and post processed.

    Any file whose type cannot be determined will simply be read then post processed.
    """
    if not isinstance(f, basestring) and filename is None:
        # Try to help figure out the file type.
        filename = getattr(f, 'name', '')
    else:
        # If user provided filename, don't override it.
        if filename is None:
            filename = f
        if not os.path.exists(filename):
            if default is not NoDefault:
                return default
            raise FullTextException('File not found')
    if not filename:
        try:
            filename = os.path.basename(f.url)
        except AttributeError:
            pass
    if type is None:
        type = get_type(filename)
    handler = FUNC_MAP.get(type, read_content)
    try:
        text = handler(f, type)
    except:
        if default is not NoDefault:
            return default
        raise
    return STRIP_WHITE.sub(' ', text).strip()


def check():
    """
    Checks for the existence of required tools, then reports missing tools to stdout. This
    can help you determine what needs to be installed for fulltext to fully function.
    """
    commands = {}
    for mimetype, cmd in PROG_MAP.items():
        commands[cmd[0][0]] = mimetype
        if cmd[1]:
            commands[cmd[1][0]] = mimetype
    for cmd, mimetype in commands.items():
        if which(cmd) is None:
            print('Cannot find command {0}, for handling {1}, please install '
                  'it.'.format(cmd, mimetype))
