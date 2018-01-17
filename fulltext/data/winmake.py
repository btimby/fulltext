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
import glob
import functools
import os
import shutil
import site
import subprocess
import sys


# --- configurable
PRJNAME = "fulltext"
HERE = os.path.abspath(os.path.dirname(__file__))
TEST_SCRIPT = 'fulltext\\test\\__init__.py'
ROOT_DIR = os.path.realpath(os.path.join(HERE, "..", ".."))
DATA_DIR = os.path.join(ROOT_DIR, PRJNAME, "data")
REQUIREMENTS_TXT = "requirements.txt"

# --- others
TEXT_WITH_NEWLINES = u"Lorem ipsum\ndolor sit amet, consectetur adipiscing e" \
                     u"lit. Nunc ipsum augue, iaculis quis\nauctor eu, adipi" \
                     u"scing non est. Nullam id sem diam, eget varius dui. E" \
                     u"tiam\nsollicitudin sapien nec odio elementum sit amet" \
                     u" luctus magna volutpat. Ut\ncommodo nulla neque. Aliq" \
                     u"uam erat volutpat. Integer et nunc augue.\nPellentesq" \
                     u"ue habitant morbi tristique senectus et netus et male" \
                     u"suada fames\nac turpis egestas. Quisque at enim nulla" \
                     u", vel tincidunt urna. Nam leo\naugue, elementum ut vi" \
                     u"verra eget, scelerisque in purus. In arcu orci, porta" \
                     u"\nnec aliquet quis, pretium a sem. In fermentum nisl " \
                     u"id diam luctus viverra.\nNullam semper, metus at euis" \
                     u"mod vulputate, orci odio dignissim urna, quis\niaculi" \
                     u"s neque lacus ut tortor. Ut a justo non dolor venenat" \
                     u"is accumsan.\nProin dolor eros, aliquam id condimentu" \
                     u"m et, aliquam quis metus. Vivamus\neget purus diam."
TEXT = TEXT_WITH_NEWLINES.replace('\n', ' ')
PYTHON = sys.executable
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
    p = subprocess.Popen(cmd, shell=True, env=os.environ, cwd=os.getcwd(),
                         stdout=subprocess.PIPE)
    out, _ = p.communicate()
    if PY3:
        out = out.decode(sys.stdout.encoding, sys.stdout.errors)
    print(out)
    if p.returncode != 0:
        sys.exit(p.returncode)
    return out


def cmd(fun):
    @functools.wraps(fun)
    def wrapper(*args, **kwds):
        return fun(*args, **kwds)

    _cmds[fun.__name__] = fun.__doc__
    return wrapper


def rm(pattern):
    """Recursively remove a file or dir by pattern."""
    paths = glob.glob(pattern)
    for path in paths:
        if path.startswith('.git/'):
            continue
        if os.path.isdir(path):
            def onerror(fun, path, excinfo):
                exc = excinfo[1]
                if exc.errno != errno.ENOENT:
                    raise

            safe_print("rmdir -f %s" % path)
            shutil.rmtree(path, onerror=onerror)
        else:
            safe_print("rm %s" % path)
            os.remove(path)


def test_setup():
    os.environ['PYTHONWARNINGS'] = 'all'


def install_pip():
    try:
        import pip  # NOQA
    except ImportError:
        sh("%s %s" % (PYTHON,
                      os.path.join(DATA_DIR, "get-pip.py")))


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
    sh('%s -c "import setuptools"' % PYTHON)
    sh("%s setup.py build" % PYTHON)
    sh("%s setup.py build_ext -i" % PYTHON)
    sh('%s -c "import %s"' % (PYTHON, PRJNAME))


@cmd
def install():
    """Install in develop / edit mode"""
    build()
    sh("%s setup.py develop" % PYTHON)


@cmd
def uninstall():
    """Uninstall %s""" % PRJNAME
    clean()
    install_pip()
    here = os.getcwd()
    try:
        os.chdir('C:\\')
        while True:
            try:
                __import__(PRJNAME, fromlist=[' '])
            except ImportError:
                break
            else:
                sh("%s -m pip uninstall -y %s" % (PYTHON, PRJNAME))
    finally:
        os.chdir(here)
        for dir in site.getsitepackages():
            for name in os.listdir(dir):
                if name.startswith(PRJNAME):
                    rm(os.path.join(dir, name))


@cmd
def clean():
    """Deletes dev files"""
    rm("$testfn*")
    rm("*.bak")
    rm("*.core")
    rm("*.egg-info")
    rm("*.orig")
    rm("*.pyc")
    rm("*.pyd")
    rm("*.pyo")
    rm("*.rej")
    rm("*.so")
    rm("*.~")
    rm("*__pycache__")
    rm(".coverage")
    rm(".tox")
    rm(".coverage")
    rm("build")
    rm("dist")
    rm("docs/_build")
    rm("htmlcov")
    rm("tmp")
    rm("venv")


@cmd
def pydeps():
    """Install useful deps"""
    install_pip()
    try:
        import setuptools  # NOQA
    except ImportError:
        sh("%s -m pip install -U setuptools" % (PYTHON))
    sh("%s -m pip install -U -r %s" % (PYTHON, REQUIREMENTS_TXT))


@cmd
def lint():
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
    sh("%s %s" % (PYTHON, TEST_SCRIPT))


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
    sh("%s -m coverage run %s" % (PYTHON, TEST_SCRIPT))
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


def venv():
    """Install venv + deps."""
    try:
        import virtualenv  # NOQA
    except ImportError:
        sh("%s -m pip install virtualenv" % PYTHON)
    if not os.path.isdir("venv"):
        sh("%s -m virtualenv venv" % PYTHON)
    sh("venv\\Scripts\\pip install -r %s" % (REQUIREMENTS_TXT))


@cmd
def pyinstaller():
    """Creates a stand alone Windows as dist/%s.exe.""" % PRJNAME
    def assertMultiLineEqual(a, b):
        import unittest
        tc = unittest.TestCase('__init__')
        tc.assertMultiLineEqual(a, b)

    def install_deps():
        sh("venv\\Scripts\\python -m pip install pyinstaller pypiwin32")
        sh("venv\\Scripts\\python -m pip install "
           "https://github.com/mattgwwalker/msg-extractor/zipball/"
           "master#egg=ExtractMsg")
        sh("venv\\Scripts\\python setup.py install")

    def run_pyinstaller():
        rm(os.path.join(ROOT_DIR, "dist"))
        bindir = os.path.join(
            DATA_DIR, "bin64" if is_windows64() else "bin32")
        assert os.path.exists(bindir), bindir
        sh("venv\\Scripts\\pyinstaller --upx-dir=%s pyinstaller.spec" % bindir)

    def check_exe():
        # Make sure the resulting .exe works.
        exe = os.path.join(ROOT_DIR, "dist", "%s.exe" % PRJNAME)
        assert os.path.exists(exe), exe
        # Test those extensions for which we know we rely on external exes.
        out = sh("%s extract %s" % (
            exe, os.path.join(ROOT_DIR, "fulltext/test/files/test.pdf")))
        assertMultiLineEqual(out.strip(), TEXT.strip())
        out = sh("%s extract %s" % (
            exe, os.path.join(ROOT_DIR, "fulltext/test/files/test.rtf")))
        assertMultiLineEqual(out.strip(), TEXT.strip())

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
