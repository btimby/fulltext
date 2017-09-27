import os
import subprocess
import errno

from os.path import isfile, dirname
from os.path import join as pathjoin

from fulltext import MissingCommandException

# TODO: Sometimes multiple tools can be used, choose the one that is installed.


class CommandLineError(Exception):
    """The traceback of all CommandLineError's is supressed when the
    errors occur on the command line to provide a useful command line
    interface.
    """
    def render(self, msg):
        return msg % vars(self)


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


# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program):
    "Simply checks if a given program exists within PATH and is executable."
    def _is_exe(fpath):
        return isfile(fpath) and os.access(fpath, os.X_OK)

    fpath = dirname(program)
    if fpath:
        if _is_exe(program):
            return program

    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = pathjoin(path, program)
            if _is_exe(exe_file):
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
        raise ShellError(' '.join(cmd), pipe.returncode, stdout, stderr)

    return stdout
