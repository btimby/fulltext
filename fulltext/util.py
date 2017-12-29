import contextlib
import atexit
import errno
import logging
import os
import subprocess
import warnings
import sys
import functools
import tempfile
import shutil
import traceback

from os.path import dirname, abspath
from os.path import join as pathjoin

import six
from six import PY3
try:
    import exiftool
except ImportError:
    exiftool = None

from fulltext.compat import which


LOGGER = logging.getLogger(__file__)
LOGGER.addHandler(logging.NullHandler())
# Get base path of this package. When running under PyInstaller, we use the
# _MEIPASS attribute of sys module, otherwise, we can simply use the parent of
# the directory containing this source file.
BASE_PATH = getattr(sys, '_MEIPASS', dirname(dirname(abspath(__file__))))
TEMPDIR = os.environ.get('FULLTEXT_TEMP', tempfile.gettempdir())


class BackendError(AssertionError):
    pass


class CommandLineError(Exception):
    """The traceback of all CommandLineError's is supressed when the
    errors occur on the command line to provide a useful command line
    interface.
    """

    def render(self, msg):
        return msg % vars(self)


class MissingCommandException(CommandLineError):

    def __init__(self, cmd, msg=""):
        self.cmd = cmd
        self.msg = msg

    def __str__(self):
        if self.msg:
            return self.msg
        else:
            return "%r CLI tool is not installed" % self.cmd


class ShellError(CommandLineError):
    """This error is raised when a shell.run returns a non-zero exit code
    (meaning the command failed).
    """

    def __init__(self, command, exit_code, stdout, stderr):
        self.command = command
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.executable = self.command.split()[0]

    def failed_message(self):
        return (
            "The command `%(command)s` failed with exit code %(exit_code)d\n"
            "------------- stdout -------------\n"
            "%(stdout)s"
            "------------- stderr -------------\n"
            "%(stderr)s"
        ) % vars(self)

    def __str__(self):
        return self.failed_message()


def run(*cmd, **kwargs):
    stdin = kwargs.get('stdin', None)
    # run a subprocess and put the stdout and stderr on the pipe object
    try:
        pipe = subprocess.Popen(
            cmd,
            stdin=stdin,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except IOError as e:
        if e.errno == errno.ENOENT:
            raise MissingCommandException(cmd[0])
        raise
    except OSError as e:
        if e.errno == errno.ENOENT:
            # File not found.
            # This is equivalent to getting exitcode 127 from sh
            raise MissingCommandException(cmd[0])

    try:
        # pipe.wait() ends up hanging on large files. using
        # pipe.communicate appears to avoid this issue
        stdout, stderr = pipe.communicate()
        if stderr:
            if PY3:
                warn(stderr.decode(sys.getfilesystemencoding(), "ignore"))
            else:
                warn(stderr)

        # if pipe is busted, raise an error (unlike Fabric)
        if pipe.returncode != 0:
            raise ShellError(' '.join(cmd), pipe.returncode, stdout, stderr)

        return stdout
    finally:
        if pipe.stdout:
            pipe.stdout.close()
        if pipe.stderr:
            pipe.stderr.close()
        try:  # Flushing a BufferedWriter may raise an error
            if pipe.stdin:
                pipe.stdin.close()
        finally:
            # Wait for the process to terminate, to avoid zombies.
            pipe.wait()


def warn(msg):
    warnings.warn(msg, UserWarning, stacklevel=2)
    LOGGER.warning(msg)


def is_windows():
    """True if the platform is Windows."""
    return 'win' in sys.platform


def is_windows64():
    """
    Determine if platform is 64 bit Windows.
    """
    return is_windows() and 'PROGRAMFILES(X86)' in os.environ


if not is_windows():
    # On linux things are simpler. Linter disabled for next line since we
    # import here for export.
    import magic  # NOQA
else:
    def _set_binpath():
        # Help the magic wrapper locate magic1.dll, we include it in
        # bin/bin{32,64}.
        bindir = 'bin64' if is_windows64() else 'bin32'
        path = pathjoin(BASE_PATH, 'bin', bindir)
        assert os.path.isdir(path), path
        os.environ['PATH'] += os.pathsep + path

    _set_binpath()

    def _import_magic():
        # Instantiate our own Magic instance so we can tell it where the
        # magic file lives.
        try:
            from magic import Magic as _Magic

            class Magic(_Magic):
                # Overridden because differently from the UNIX version
                # the Windows version does not provide mime kwarg.
                def from_file(self, filename, mime=True):
                    return _Magic.from_file(self, filename)

                def from_buffer(self, buf, mime=True):
                    return _Magic.from_buffer(self, buf)

            return Magic(mime=True,
                         magic_file=pathjoin(BASE_PATH, 'bin', 'magic'))
        except Exception:
            traceback.print_exc()
            warnings.warn('Magic is unavailable, type detection degraded')
            return None

    magic = _import_magic()


def assert_cmd_exists(cmd):
    if not which(cmd):
        raise MissingCommandException(cmd)


def memoize(fun):
    """A simple memoize decorator for functions supporting (hashable)
    positional arguments.
    It also provides a cache_clear() function for clearing the cache:

    >>> @memoize
    ... def foo()
    ...     return 1
        ...
    >>> foo()
    1
    >>> foo.cache_clear()
    >>>
    """
    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        key = (args, frozenset(sorted(kwargs.items())))
        try:
            return cache[key]
        except KeyError:
            ret = cache[key] = fun(*args, **kwargs)
            return ret

    def cache_clear():
        """Clear cache."""
        cache.clear()

    cache = {}
    wrapper.cache_clear = cache_clear
    return wrapper


@memoize
def term_supports_colors():
    try:
        import curses
        assert sys.stderr.isatty()
        curses.setupterm()
        assert curses.tigetnum("colors") > 0
    except Exception:
        return False
    else:
        return True


def hilite(s, ok=True, bold=False):
    """Return an highlighted version of 'string'."""
    if not term_supports_colors():
        return s
    attr = []
    if ok is None:  # no color
        pass
    elif ok:   # green
        attr.append('32')
    else:   # red
        attr.append('31')
    if bold:
        attr.append('1')
    return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), s)


def is_file_path(obj):
    """Return True if obj is a possible file path or name."""
    return isinstance(obj, six.string_types) or isinstance(obj, bytes)


@contextlib.contextmanager
def fobj_to_tempfile(f, suffix=''):
    """Context manager which copies a file object to disk and return its
    name. When done the file is deleted.
    """
    with tempfile.NamedTemporaryFile(
            dir=TEMPDIR, suffix=suffix, delete=False) as t:
        shutil.copyfileobj(f, t)
    try:
        yield t.name
    finally:
        os.remove(t.name)


if exiftool is not None:
    _et = exiftool.ExifTool()
    _et.start()

    @atexit.register
    def _close_et():
        LOGGER.debug("terminating exiftool subprocess")
        _et.terminate()

    def exiftool_title(path, encoding, encoding_error):
        if is_file_path(path):
            title = (_et.get_tag("title", path) or "").strip()
            if title:
                if hasattr(title, "decode"):  # PY2
                    return title.decode(encoding, encoding_error)
                else:
                    return title

else:
    # TODO: according to https://www.sno.phy.queensu.ca/~phil/exiftool/
    # exiftool is also available on Windows
    def exiftool_title(*a, **kw):
        return None
