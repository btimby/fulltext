#!/usr/bin/env python

# Copyright (c) 2009 Giampaolo Rodola'. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


"""Shortcuts for various tasks, emulating UNIX "make" on Windows.
This is supposed to be invoked by "make.bat" and not used directly.
This was originally written as a bat file but they suck so much
that they should be deemed illegal!
"""

from __future__ import print_function
import errno
import fnmatch
import functools
import os
import shutil
import site
import subprocess
import sys


PYTHON = sys.executable
TSCRIPT = 'tests.py'
HERE = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.realpath(os.path.join(HERE, "..", ".."))
PY3 = sys.version_info[0] == 3
_cmds = {}
if PY3:
    basestring = str

# ===================================================================
# utils
# ===================================================================


def safe_print(text, file=sys.stdout, flush=False):
    """Prints a (unicode) string to the console, encoded depending on
    the stdout/file encoding (eg. cp437 on Windows). This is to avoid
    encoding errors in case of funky path names.
    Works with Python 2 and 3.
    """
    if not isinstance(text, basestring):
        return print(text, file=file)
    try:
        file.write(text)
    except UnicodeEncodeError:
        bytes_string = text.encode(file.encoding, 'backslashreplace')
        if hasattr(file, 'buffer'):
            file.buffer.write(bytes_string)
        else:
            text = bytes_string.decode(file.encoding, 'strict')
            file.write(text)
    file.write("\n")


def sh(cmd, nolog=False):
    if not nolog:
        safe_print("cmd: " + cmd)
    p = subprocess.Popen(cmd, shell=True, env=os.environ, cwd=os.getcwd())
    p.communicate()
    if p.returncode != 0:
        sys.exit(p.returncode)


def cmd(fun):
    @functools.wraps(fun)
    def wrapper(*args, **kwds):
        return fun(*args, **kwds)

    _cmds[fun.__name__] = fun.__doc__
    return wrapper


def rm(pattern, directory=False):
    """Recursively remove a file or dir by pattern."""
    def safe_remove(path):
        try:
            os.remove(path)
        except OSError as err:
            if err.errno != errno.ENOENT:
                raise
        else:
            safe_print("rm %s" % path)

    def safe_rmtree(path):
        def onerror(fun, path, excinfo):
            exc = excinfo[1]
            if exc.errno != errno.ENOENT:
                raise

        existed = os.path.isdir(path)
        shutil.rmtree(path, onerror=onerror)
        if existed:
            safe_print("rmdir -f %s" % path)

    if "*" not in pattern:
        if directory:
            safe_rmtree(pattern)
        else:
            safe_remove(pattern)
        return

    for root, subdirs, subfiles in os.walk('.'):
        root = os.path.normpath(root)
        if root.startswith('.git/'):
            continue
        found = fnmatch.filter(subdirs if directory else subfiles, pattern)
        for name in found:
            path = os.path.join(root, name)
            if directory:
                safe_print("rmdir -f %s" % path)
                safe_rmtree(path)
            else:
                safe_print("rm %s" % path)
                safe_remove(path)


def safe_remove(path):
    try:
        os.remove(path)
    except OSError as err:
        if err.errno != errno.ENOENT:
            raise
    else:
        safe_print("rm %s" % path)


def safe_rmtree(path):
    def onerror(fun, path, excinfo):
        exc = excinfo[1]
        if exc.errno != errno.ENOENT:
            raise

    existed = os.path.isdir(path)
    shutil.rmtree(path, onerror=onerror)
    if existed:
        safe_print("rmdir -f %s" % path)


def recursive_rm(*patterns):
    """Recursively remove a file or matching a list of patterns."""
    for root, subdirs, subfiles in os.walk(u'.'):
        root = os.path.normpath(root)
        if root.startswith('.git/'):
            continue
        for file in subfiles:
            for pattern in patterns:
                if fnmatch.fnmatch(file, pattern):
                    safe_remove(os.path.join(root, file))
        for dir in subdirs:
            for pattern in patterns:
                if fnmatch.fnmatch(dir, pattern):
                    safe_rmtree(os.path.join(root, dir))


def test_setup():
    os.environ['PYTHONWARNINGS'] = 'all'


# ===================================================================
# commands
# ===================================================================


@cmd
def help():
    """Print this help"""
    safe_print('Run "make [-p <PYTHON>] <target>" where <target> is one of:')
    for name in sorted(_cmds):
        safe_print(
            "    %-20s %s" % (name.replace('_', '-'), _cmds[name] or ''))
    sys.exit(1)


@cmd
def build():
    """Build / compile"""
    # Make sure setuptools is installed (needed for 'develop' /
    # edit mode).
    generate_manifest()
    sh('%s -c "import setuptools"' % PYTHON)
    sh("%s setup.py build" % PYTHON)
    sh("%s setup.py build_ext -i" % PYTHON)
    sh('%s -c "import fulltext"' % PYTHON)


@cmd
def generate_manifest():
    """Update MANIFEST.in file."""
    genman_py = os.path.join(HERE, "generate_manifest.py")
    manifest = os.path.join(ROOT_DIR, 'MANIFEST.in')
    assert os.path.exists(genman_py), genman_py
    assert os.path.exists(manifest), manifest
    out = subprocess.check_output([PYTHON, genman_py])
    if PY3:
        out = out.decode(sys.getfilesystemencoding())
    with open(manifest, "wt") as f:
        for line in out.splitlines():
            f.write(line + '\n')


@cmd
def install():
    """Install in develop / edit mode"""
    build()
    sh("%s setup.py develop" % PYTHON)


@cmd
def uninstall():
    """Uninstall fulltext"""
    clean()
    install_pip()
    here = os.getcwd()
    try:
        os.chdir('C:\\')
        while True:
            try:
                import fulltext  # NOQA
            except ImportError:
                break
            else:
                sh("%s -m pip uninstall -y fulltext" % PYTHON)
    finally:
        os.chdir(here)

    for dir in site.getsitepackages():
        for name in os.listdir(dir):
            if name.startswith('fulltext'):
                rm(os.path.join(dir, name))


@cmd
def clean():
    """Deletes dev files"""
    recursive_rm(
        "$testfn*",
        "*.bak",
        "*.core",
        "*.egg-info",
        "*.orig",
        "*.pyc",
        "*.pyd",
        "*.pyo",
        "*.rej",
        "*.so",
        "*.~",
        "*__pycache__",
        ".coverage",
        ".tox",
    )
    safe_rmtree(".coverage")
    safe_rmtree("build")
    safe_rmtree("dist")
    safe_rmtree("docs/_build")
    safe_rmtree("htmlcov")
    safe_rmtree("tmp")
    safe_rmtree("venv")
    safe_rmtree("venv2")
    safe_rmtree("venv3")


@cmd
def pydeps():
    """Install useful deps"""
    install_pip()
    sh("%s -m pip install -U setuptools" % (PYTHON))
    sh("%s -m pip install -U -r requirements.txt" % (PYTHON))


@cmd
def flake8():
    """Run flake8 against all py files"""
    py_files = subprocess.check_output("git ls-files")
    if PY3:
        py_files = py_files.decode()
    py_files = [x for x in py_files.split() if x.endswith('.py')]
    py_files = ' '.join(py_files)
    sh("%s -m flake8 %s" % (PYTHON, py_files), nolog=True)


@cmd
def test():
    """Run tests"""
    install()
    test_setup()
    sh("%s %s" % (PYTHON, TSCRIPT))


@cmd
def ci():
    """Run CI tests."""
    pydeps()
    test()
    pyinstaller()


@cmd
def coverage():
    """Run coverage tests."""
    # Note: coverage options are controlled by .coveragerc file
    install()
    test_setup()
    sh("%s -m coverage run %s" % (PYTHON, TSCRIPT))
    sh("%s -m coverage report" % PYTHON)
    sh("%s -m coverage html" % PYTHON)
    sh("%s -m webbrowser -t htmlcov/index.html" % PYTHON)


@cmd
def test_by_name():
    """Run test by name"""
    try:
        safe_print(sys.argv)
        name = sys.argv[2]
    except IndexError:
        sys.exit('second arg missing')
    install()
    test_setup()
    sh("%s -m unittest -v %s" % (PYTHON, name))


def set_python(s):
    global PYTHON
    if os.path.isabs(s):
        PYTHON = s
    else:
        # try to look for a python installation
        orig = s
        s = s.replace('.', '')
        vers = ('26', '27', '34', '35', '36', '37',
                '26-64', '27-64', '34-64', '35-64', '36-64', '37-64')
        for v in vers:
            if s == v:
                path = 'C:\\python%s\\python.exe' % s
                if os.path.isfile(path):
                    print(path)
                    PYTHON = path
                    os.putenv('PYTHON', path)
                    return
        return sys.exit(
            "can't find any python installation matching %r" % orig)


def is_windows64():
    return 'PROGRAMFILES(X86)' in os.environ


@cmd
def venv():
    """Install venv + deps."""
    sh("%s -m pip install virtualenv" % PYTHON)
    sh("%s -m virtualenv venv" % PYTHON)
    sh("venv\\Scripts\\pip install -r requirements.txt")


@cmd
def pyinstaller():
    """Creates a stand alone Windows exe (dist/duster.exe)."""
    def install_deps():
        sh("venv\\Scripts\\python -m pip install pyinstaller pypiwin32")
        sh("venv\\Scripts\\python setup.py install")

    def run_pyinstaller():
        rm(os.path.join(ROOT_DIR, "dist"), directory=True)
        bindir = os.path.join(
            ROOT_DIR, "fulltext\\data\\bin64\\" if is_windows64()
            else "fulltext\\data\\bin\\bin32\\")
        assert os.path.exists(bindir), bindir
        sh("venv\\Scripts\\pyinstaller --upx-dir=%s pyinstaller.spec" % bindir)

    def check_exe():
        # Make sure the resulting .exe works.
        path = os.path.join(ROOT_DIR, "dist", "fulltext.exe")
        assert os.path.exists(path), path
        out = sh("%s extract setup.py" % path)
        safe_print(out)

    venv()
    install_deps()
    run_pyinstaller()
    check_exe()


def parse_cmdline():
    if '-p' in sys.argv:
        try:
            pos = sys.argv.index('-p')
            sys.argv.pop(pos)
            py = sys.argv.pop(pos)
        except IndexError:
            return help()
        set_python(py)


def main():
    parse_cmdline()
    try:
        cmd = sys.argv[1].replace('-', '_')
    except IndexError:
        return help()
    if cmd in _cmds:
        fun = getattr(sys.modules[__name__], cmd)
        fun()
    else:
        help()


if __name__ == '__main__':
    main()
