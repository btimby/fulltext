import os
import re
import csv
import os.path
import tempfile
import mimetypes
import subprocess
import errno

from fulltext import MissingCommandException

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

# TODO: Sometimes multiple tools can be used, choose the one that is installed.


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


def run(*cmd, **kwargs):
    stdin = kwargs.get('stdin', None)
    # run a subprocess and put the stdout and stderr on the pipe object
    try:
        pipe = subprocess.Popen(
            cmd,
            stdin=stdin,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except OSError as e:
        if e.errno == errno.ENOENT:
            # File not found.
            # This is equivalent to getting exitcode 127 from sh
            raise MissingCommandException(cmd[0])

    # pipe.wait() ends up hanging on large files. using
    # pipe.communicate appears to avoid this issue
    stdout, stderr = pipe.communicate()

    # if pipe is busted, raise an error (unlike Fabric)
    if pipe.returncode != 0:
        raise exceptions.ShellError(
            ' '.join(args), pipe.returncode, stdout, stderr,
        )

    return stdout
