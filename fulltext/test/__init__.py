#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest
import tempfile
import sys
import subprocess
import logging
try:
    from unittest import mock  # py3
except ImportError:
    import mock  # NOQA - requires "pip install mock"

from os.path import join as pathjoin
import codecs
import difflib
import textwrap

import fulltext
from fulltext.util import is_windows
from fulltext.magicwrap import MagicWrapper
from fulltext.magicwrap import PuremagicWrapper
from fulltext.util import exiftool
from fulltext.compat import which

from six import PY3
from six import BytesIO


TRAVIS = bool(os.environ.get('TRAVIS'))
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
WINDOWS = is_windows()
APPVEYOR = bool(os.environ.get('APPVEYOR'))
HERE = os.path.abspath(os.path.dirname(__file__))

logging.basicConfig(level=logging.WARNING)


# ===================================================================
# --- Utils
# ===================================================================


class BaseTestCase(unittest.TestCase):
    """Base TestCase Class."""

    # --- override

    def __str__(self):
        # Print fully qualified test name.
        return "%s.%s.%s" % (
            os.path.splitext(__file__)[0], self.__class__.__name__,
            self._testMethodName)

    def shortDescription(self):
        # Avoid printing docstrings.
        return ""

    # --- utils

    def touch(self, fname, content=None):
        if isinstance(content, bytes):
            f = open(fname, "wb")
        else:
            if PY3:
                f = open(fname, "wt")
            else:
                f = codecs.open(fname, "wt", encoding="utf8")

        self.addCleanup(os.remove, fname)
        with f:
            if content:
                f.write(content)

        return fname

    def touch_fobj(self, content=b""):
        f = BytesIO()
        self.addCleanup(f.close)
        if content:
            f.write(content)
            f.seek(0)
        return f

    def assertMultiLineEqual(self, a, b, msg=None):
        """A useful assertion for troubleshooting."""
        # Normalize spacing/formatting.
        a = textwrap.wrap(a)
        b = textwrap.wrap(b)

        # Check if two blocks of text are equal.
        if a == b:
            return

        if msg is None:
            # If not the same, and no msg provided, create a user-friendly
            # diff message.
            a = [l + '\n' for l in a]
            b = [l + '\n' for l in b]
            msg = '\n' + ''.join(difflib.unified_diff(
                a, b, 'A (first argument)', 'B (second argument)'))

        raise AssertionError(msg)

    def assertStartsWith(self, prefix, body):
        """Shortcut."""
        if not body.startswith(prefix):
            msg = '"%s" != "%s"' % (body[:len(prefix)], prefix)
            raise AssertionError(msg)

    def assertEndsWith(self, postfix, body):
        """Shortcut."""
        if not body.endswith(postfix):
            msg = '"%s" != "%s"' % (body[0 - len(postfix):], postfix)
            raise AssertionError(msg)


unittest.TestCase = BaseTestCase


# ===================================================================
# --- Tests
# ===================================================================


class FullTextTestCase(BaseTestCase):

    def test_missing_default(self):
        "Ensure a missing file returns default instead of exception."
        self.assertEqual(fulltext.get('non-existent-file.pdf', 'sentinal'),
                         'sentinal')

    def test_missing(self):
        "Ensure a missing file without a default raises an exception."
        # In this case we hit the pdf backend which runs a command, the
        # command fails because the file does not exist resulting in
        # ShellError.
        self.assertRaises(IOError, fulltext.get, 'non-existent-file.txt')

    def test_unknown_default(self):
        "Ensure unknown file type returns default instead of exception."
        self.assertEqual(fulltext.get('unknown-file.foobar', 'sentinal'),
                         'sentinal')

    def test_unknown(self):
        "Ensure unknown file type without a default raises an exception."
        # This is nearly a duplicate of test_missing, but in this case we hit
        # the default text backend, which attempts to open the file resulting
        # in an IOError.
        self.assertRaises(IOError, fulltext.get, 'unknown-file.foobar')

    def test_default_none(self):
        "Ensure None is a valid value to pass as default."
        self.assertEqual(fulltext.get('unknown-file.foobar', None), None)

    def test_text_strip(self):
        """Ensure that stripping works as expected."""
        file = BytesIO()
        file.write(b'  Test leading and trailing spaces removal.  ')
        file.write(b'Test @$%* punctuation removal! ')
        file.write(b'Test    spaces     removal! ')
        file.seek(0)
        stripped = fulltext.get(file, backend='bin')
        self.assertMultiLineEqual('Test leading and trailing spaces removal. '
                                  'Test punctuation removal! Test spaces '
                                  'removal!', stripped)

    def test_register_backend_ext(self):
        fulltext.register_backend(
            'application/ijustmadethisup',
            'fulltext.backends.__html',
            extensions=['.ijustmadethisup'])

        fname = self.touch("document.ijustmadethisup")
        with mock.patch('fulltext.handle_path', return_value="") as m:
            fulltext.get(fname)
            klass = m.call_args[0][0]
            self.assertEqual(klass.__module__, 'fulltext.backends.__html')

    def test_text_ext(self):
        for ext in (".py", ".cpp", ".h", ".pl"):
            fname = self.touch("document%s" % ext)
            with mock.patch('fulltext.handle_path', return_value="") as m:
                fulltext.get(fname)
                klass = m.call_args[0][0]
                self.assertEqual(klass.__module__, 'fulltext.backends.__text')


class TestCLI(BaseTestCase):

    def test_extract(self):
        subprocess.check_output(
            "%s -m fulltext extract %s" % (
                sys.executable, pathjoin(HERE, "files/test.txt")),
            shell=True)

    def test_check(self):
        p = subprocess.Popen(
            "%s -m fulltext -t check" % sys.executable, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            if not WINDOWS:
                # Everything is supposed to work on Linux.
                self.fail(err.decode())
            else:
                # On Windows we expect a bunch of backends not to work.
                # XXX maybe this is too strict.
                lines = [x.split(':')[0] for x in
                         sorted(err.decode().splitlines())
                         if x.split(':')[0].startswith('fulltext.')]
                self.assertEqual(
                    lines,
                    ['fulltext.backends.__doc',
                     'fulltext.backends.__hwp',
                     'fulltext.backends.__ocr',
                     'fulltext.backends.__ps'])

    @unittest.skipIf(not WINDOWS, "windows only")
    def test_which(self):
        self.assertIsNotNone(which("pdftotext"))
        self.assertIsNotNone(which("unrtf"))
        self.assertIsNotNone(which("unrar"))
        self.assertIsNotNone(which("exiftool"))


class TestBackendInterface(BaseTestCase):

    def test_params(self):
        # Make sure Backend class receives the right params.
        fname = self.touch('testfn.doc')
        with mock.patch('fulltext.handle_path', return_value="") as m:
            fulltext.get(fname, encoding='foo', encoding_errors='bar')
            klass = m.call_args[0][0]
            self.assertEqual(klass.encoding, 'foo')
            self.assertEqual(klass.encoding_errors, 'bar')

    def test_callbacks(self):
        # Make sure callback methods are called (also in the right order).
        flags = []

        class Backend:

            def setup(self):
                flags.append("setup")

            def teardown(self):
                flags.append("teardown")

            def handle_fobj(self, path):
                flags.append("handle_fobj")
                return "text"

        fname = self.touch('testfn.doc')
        with mock.patch('fulltext.backend_inst_from_mod',
                        return_value=Backend()):
            fulltext.get(fname, encoding='foo', encoding_errors='bar')
        self.assertEqual(flags, ['setup', 'handle_fobj', 'teardown'])

    def test_teardown_on_err(self):
        # Make sure teardown methods is called also on error.
        flags = []

        class Backend:

            def setup(self):
                flags.append("setup")

            def teardown(self):
                flags.append("teardown")

            def handle_fobj(self, path):
                1 / 0

        fname = self.touch('testfn.doc')
        with mock.patch('fulltext.backend_inst_from_mod',
                        return_value=Backend()):
            with self.assertRaises(ZeroDivisionError):
                fulltext.get(fname, encoding='foo', encoding_errors='bar')

        self.assertEqual(flags, ['setup', 'teardown'])


class TestInstalledDeps(BaseTestCase):
    """Make sure certain deps are installed."""

    def test_exiftool(self):
        self.assertIsNotNone(exiftool)


# ===================================================================
# --- Mixin tests
# ===================================================================


class PathAndFileTests(object):
    text = TEXT
    mime = None

    def test_file(self):
        path = pathjoin(HERE, 'files/test.%s' % self.ext)
        with open(path, 'rb') as f:
            text = fulltext.get(f, mime=self.mime)
            self.assertMultiLineEqual(self.text, text)

    def _handle_text(self, f):
        """Main body of both 'text mode' tests."""
        try:
            text = fulltext.get(f, mime=self.mime)
            self.assertMultiLineEqual(self.text, text)
        finally:
            f.close()

    def test_file_text(self):
        path = pathjoin(HERE, 'files/test.%s' % self.ext)
        if PY3:
            with self.assertRaises(AssertionError):
                self._handle_text(open(path, 'rt'))
        else:
            self._handle_text(open(path, 'rt'))

    def test_file_codecs(self):
        path = pathjoin(HERE, 'files/test.%s' % self.ext)
        with self.assertRaises(AssertionError):
            self._handle_text(codecs.open(path, encoding='utf8'))

    def test_path(self):
        path = pathjoin(HERE, 'files/test.%s' % self.ext)
        text = fulltext.get(path, mime=self.mime)
        self.assertMultiLineEqual(self.text, text)


class TxtTestCase(BaseTestCase, PathAndFileTests):
    ext = 'txt'


class OdtTestCase(BaseTestCase, PathAndFileTests):
    ext = 'odt'


@unittest.skipIf(WINDOWS, "not supported on Windows")
class DocTestCase(BaseTestCase, PathAndFileTests):
    ext = "doc"


class DocxTestCase(BaseTestCase, PathAndFileTests):
    ext = "docx"


class OdsTestCase(BaseTestCase, PathAndFileTests):
    ext = "ods"


class XlsTestCase(BaseTestCase, PathAndFileTests):
    ext = "xls"


class XlsxTestCase(BaseTestCase, PathAndFileTests):
    ext = "xlsx"


class HtmlTestCase(BaseTestCase, PathAndFileTests):
    ext = "html"


class XmlTestCase(BaseTestCase, PathAndFileTests):
    ext = "xml"


class ZipTestCase(BaseTestCase, PathAndFileTests):
    ext = "zip"


class PdfTestCase(BaseTestCase, PathAndFileTests):
    ext = "pdf"


class RarTestCase(BaseTestCase, PathAndFileTests):
    ext = "rar"


class RtfTestCase(BaseTestCase, PathAndFileTests):
    ext = "rtf"


class CsvTestCase(BaseTestCase, PathAndFileTests):
    ext = "csv"
    mime = 'text/csv'
    text = TEXT.replace(',', '')

    def test_newlines(self):
        # See: https://github.com/btimby/fulltext/issues/68
        fname = self.touch('testfn.csv', content="foo\n\rbar")
        self.assertEqual(fulltext.get(fname), "foo bar")


class TsvTestCase(BaseTestCase, PathAndFileTests):
    ext = "tsv"
    mime = 'text/tsv'


class PsvTestCase(BaseTestCase, PathAndFileTests):
    ext = "psv"
    mime = 'text/psv'


@unittest.skipIf(WINDOWS, "not supported on Windows")
class PngTestCase(BaseTestCase, PathAndFileTests):
    ext = "png"


class EpubTestCase(BaseTestCase, PathAndFileTests):
    ext = "epub"


@unittest.skipIf(WINDOWS, "not supported on Windows")
class PsTestCase(BaseTestCase, PathAndFileTests):
    ext = "ps"


class EmlTestCase(BaseTestCase, PathAndFileTests):
    ext = "eml"


class MboxTestCase(BaseTestCase, PathAndFileTests):
    ext = "mbox"


class MsgTestCase(BaseTestCase, PathAndFileTests):
    ext = "msg"


class JsonTestCase(BaseTestCase, PathAndFileTests):
    ext = "json"


@unittest.skipIf(not which('pyhwp'), "pyhwp not installed")
class HwpTestCase(BaseTestCase, PathAndFileTests):
    ext = "hwp"


class GzTestCase(BaseTestCase, PathAndFileTests):
    ext = "gz"

    def test_pdf(self):
        # See: https://github.com/btimby/fulltext/issues/56
        text = fulltext.get(pathjoin(HERE, "files/gz/test.pdf.gz"))
        self.assertMultiLineEqual(self.text, text)

    def test_csv(self):
        text = fulltext.get(pathjoin(HERE, "files/gz/test.csv.gz"))
        self.assertMultiLineEqual(self.text.replace(',', ''), text)

    def test_txt(self):
        text = fulltext.get(pathjoin(HERE, "files/gz/test.txt.gz"))
        self.assertMultiLineEqual(self.text, text)


# ---


class FilesTestCase(BaseTestCase):

    @unittest.skipIf(WINDOWS, "not supported on Windows")
    def test_old_doc_file(self):
        "Antiword does not support older Word documents."
        with open(pathjoin(HERE, 'files/test.old.doc'), 'rb') as f:
            text = fulltext.get(f, backend='doc')
            self.assertStartsWith('eZ-Audit', text)
            self.assertIsInstance(text, u"".__class__)

    @unittest.skipIf(WINDOWS, "not supported on Windows")
    def test_old_doc_path(self):
        "Antiword does not support older Word documents."
        text = fulltext.get(pathjoin(HERE, 'files/test.old.doc'),
                            backend='doc')
        self.assertStartsWith('eZ-Audit', text)
        self.assertIsInstance(text, u"".__class__)


# ===================================================================
# --- Pickups
# ===================================================================


class TestPickups(BaseTestCase):
    """Make sure the right backend is called."""

    # --- by extension

    def test_by_ext(self):
        fname = self.touch('testfn.html')
        with mock.patch('fulltext.handle_path', return_value="") as m:
            fulltext.get(fname)
            klass = m.call_args[0][0]
            self.assertEqual(klass.__module__, 'fulltext.backends.__html')

    def test_no_ext(self):
        # File with no extension == use bin backend.
        fname = self.touch('testfn')
        with mock.patch('fulltext.handle_path', return_value="") as m:
            fulltext.get(fname)
            klass = m.call_args[0][0]
            self.assertEqual(klass.__module__, 'fulltext.backends.__bin')

    def test_unknown_ext(self):
        # File with unknown extension == use bin backend.
        fname = self.touch('testfn.unknown')
        with mock.patch('fulltext.handle_path', return_value="") as m:
            fulltext.get(fname)
            klass = m.call_args[0][0]
            self.assertEqual(klass.__module__, 'fulltext.backends.__bin')

    # --- by mime opt

    def test_by_mime(self):
        fname = self.touch('testfn.doc')
        with mock.patch('fulltext.handle_path', return_value="") as m:
            fulltext.get(fname, mime='application/vnd.ms-excel')
            klass = m.call_args[0][0]
            self.assertEqual(klass.__module__, 'fulltext.backends.__xlsx')

    def test_by_unknown_mime(self):
        fname = self.touch('testfn.doc')
        with mock.patch('fulltext.handle_path', return_value="") as m:
            fulltext.get(fname, mime='application/yo!')
            klass = m.call_args[0][0]
            self.assertEqual(klass.__module__, 'fulltext.backends.__bin')

    # -- by name opt

    @unittest.skipIf(WINDOWS, "not supported on Windows")
    def test_by_name(self):
        fname = self.touch('testfn')
        with mock.patch('fulltext.handle_path', return_value="") as m:
            fulltext.get(fname, name="woodstock.doc")
            klass = m.call_args[0][0]
            self.assertEqual(klass.__module__, 'fulltext.backends.__doc')

    def test_by_name_with_no_ext(self):
        # Assume bin backend is picked up.
        fname = self.touch("woodstock-no-ext")
        with mock.patch('fulltext.handle_path', return_value="") as m:
            fulltext.get(fname, name=fname)
            klass = m.call_args[0][0]
            self.assertEqual(klass.__module__, 'fulltext.backends.__bin')

    # --- by backend opt

    def test_by_backend(self):
        # Assert file ext is ignored if backend opt is used.
        fname = self.touch('testfn.doc')
        with mock.patch('fulltext.handle_path', return_value="") as m:
            fulltext.get(fname, backend='html')
            klass = m.call_args[0][0]
            self.assertEqual(klass.__module__, 'fulltext.backends.__html')

    def test_by_invalid_backend(self):
        # Assert file ext is ignored if backend opt is used.
        fname = self.touch('testfn.doc')
        with self.assertRaises(ValueError):
            fulltext.get(fname, backend='yoo')

    # --- by src code ext

    def test_src_code_ext(self):
        fname = "file.js"
        self.touch(fname, content="foo bar")
        with mock.patch('fulltext.handle_path', return_value="") as m:
            fulltext.get(fname)
            klass = m.call_args[0][0]
            self.assertEqual(klass.__module__, 'fulltext.backends.__text')


# ===================================================================
# --- File objects
# ===================================================================


class TestFileObj(BaseTestCase):

    def test_returned_content(self):
        f = self.touch_fobj(content=b"hello world")
        ret = fulltext.get(f)
        self.assertEqual(ret, "hello world")

    def test_name_attr(self):
        # Make sure that fulltext attempts to determine file name
        # from "name" attr of the file obj.
        f = tempfile.NamedTemporaryFile(suffix='.html')
        with mock.patch('fulltext.handle_fobj', return_value="") as m:
            fulltext.get(f)
            klass = m.call_args[0][0]
            self.assertEqual(klass.__module__, 'fulltext.backends.__html')

    @unittest.skipIf(WINDOWS, "not supported on Windows")
    def test_fobj_offset(self):
        # Make sure offset is unaltered after guessing mime type.
        f = self.touch_fobj(content=b"hello world")
        f.seek(0)
        mod = fulltext.backend_from_fobj(f)
        self.assertEqual(mod.__name__, 'fulltext.backends.__text')


class TestGuessingFromFileContent(BaseTestCase):
    """Make sure that when file has no extension its type is guessed
    from its content.
    """

    def test_pdf(self):
        fname = "file-noext"
        with open(pathjoin(HERE, 'files/test.pdf'), 'rb') as f:
            data = f.read()
        self.touch(fname, content=data)
        with mock.patch('fulltext.handle_path', return_value="") as m:
            fulltext.get(fname)
            klass = m.call_args[0][0]
            if WINDOWS:
                self.assertEqual(klass.__module__, 'fulltext.backends.__bin')
            else:
                self.assertEqual(klass.__module__, 'fulltext.backends.__pdf')

    @unittest.skipIf(WINDOWS, "not supported on Windows")
    def test_html(self):
        fname = "file-noext"
        self.touch(fname, content=open(
            pathjoin(HERE, 'files/test.html'), 'rb').read())
        with mock.patch('fulltext.handle_path', return_value="") as m:
            fulltext.get(fname)
            klass = m.call_args[0][0]
            self.assertEqual(klass.__module__, 'fulltext.backends.__html')


class TestUtils(BaseTestCase):

    def test_is_file_path(self):
        from fulltext.util import is_file_path
        assert is_file_path('foo')
        assert is_file_path(b'foo')
        with open(__file__) as f:
            assert not is_file_path(f)


# ===================================================================
# --- Encodings
# ===================================================================


class TestEncodingGeneric(BaseTestCase):

    def test_global_vars(self):
        # Make sure the globla vars are taken into consideration and
        # passed to the underlying backends.
        encoding, errors = fulltext.ENCODING, fulltext.ENCODING_ERRORS
        fname = self.touch("file.txt", content=b"hello")
        try:
            fulltext.ENCODING = "foo"
            fulltext.ENCODING_ERRORS = "bar"
            with mock.patch('fulltext.handle_path', return_value="") as m:
                fulltext.get(fname)
                klass = m.call_args[0][0]
                self.assertEqual(klass.encoding, 'foo')
                self.assertEqual(klass.encoding_errors, 'bar')
        finally:
            fulltext.ENCODING = encoding
            fulltext.ENCODING_ERRORS = errors


@unittest.skipIf(WINDOWS, "not supported on Windows")
class TestUnicodeBase(object):
    ext = None
    italian = u"ciao bella àèìòù "
    japanese = u"かいおうせい海王星"
    invalid = u"helloworld"

    def compare(self, content_s, fulltext_s):
        if PY3:
            self.assertEqual(content_s, fulltext_s)
        else:
            # Don't test for equality on Python 2 because unicode
            # support is basically broken.
            self.assertEqual(content_s, fulltext_s)
            pass

    def doit(self, fname, expected_txt):
        ret = fulltext.get(fname)
        self.compare(ret, expected_txt)

    def test_italian(self):
        self.doit(pathjoin(HERE, "files/unicode/it.%s" % self.ext),
                  self.italian)

    def test_japanese(self):
        self.doit(pathjoin(HERE, "files/unicode/jp.%s" % self.ext),
                  self.japanese)

    def test_invalid_char(self):
        fname = pathjoin(HERE, "files/unicode/invalid.%s" % self.ext)
        if os.path.exists(fname):
            with self.assertRaises(UnicodeDecodeError):
                fulltext.get(fname)
            ret = fulltext.get(fname, encoding_errors="ignore")
            self.assertEqual(ret, self.invalid)
        #
        fname = pathjoin(HERE, "files/unicode/it.%s" % self.ext)
        with self.assertRaises(UnicodeDecodeError):
            fulltext.get(fname, encoding='ascii')
        ret = fulltext.get(
            fname, encoding='ascii', encoding_errors="ignore")
        against = self.italian.replace(
            u"àèìòù", u"").replace(u"  ", u" ").strip()
        self.assertEqual(ret, against)


class TestUnicodeTxt(BaseTestCase, TestUnicodeBase):
    ext = "txt"


class TestUnicodeCsv(BaseTestCase, TestUnicodeBase):
    ext = "csv"


class TestUnicodeOdt(BaseTestCase, TestUnicodeBase):
    ext = "odt"

    # A binary file is passed and text is not de/encoded.
    @unittest.skipIf(1, "no conversion happening")
    def test_invalid_char(self):
        pass


# ps backend uses `pstotext` CLI tool, which does not correctly
# handle unicode. Just make sure we don't crash if passed the
# error handler.
@unittest.skipIf(WINDOWS, "not supported on Windows")
class TestUnicodePs(BaseTestCase):

    def test_italian(self):
        fname = pathjoin(HERE, "files/unicode/it.ps")
        with self.assertRaises(UnicodeDecodeError):
            fulltext.get(fname)
        ret = fulltext.get(fname, encoding_errors="ignore")
        assert ret.startswith("ciao bella")  # the rest is garbage


class TestUnicodeHtml(BaseTestCase, TestUnicodeBase):
    ext = "html"


# backend uses `unrtf` CLI tool, which does not correctly
# handle unicode. Just make sure we don't crash if passed the
# error handler.
@unittest.skipIf(WINDOWS, "not supported on Windows")
class TestUnicodeRtf(BaseTestCase):
    ext = "rtf"

    def test_italian(self):
        fname = pathjoin(HERE, "files/unicode/it.rtf")
        with self.assertRaises(UnicodeDecodeError):
            fulltext.get(fname)
        ret = fulltext.get(fname, encoding_errors="ignore")
        assert ret.startswith("ciao bella")  # the rest is garbage


class TestUnicodeDoc(BaseTestCase, TestUnicodeBase):
    ext = "doc"
    italian = ' '.join([u"ciao bella àèìòù" for x in range(20)])
    japanese = ' '.join([u"かいおうせい海王星" for x in range(30)])


class TestUnicodeXml(BaseTestCase, TestUnicodeBase):
    ext = "xml"


class TestUnicodeXlsx(BaseTestCase, TestUnicodeBase):
    ext = "xlsx"

    # A binary file is passed and text is not de/encoded.
    @unittest.skipIf(1, "no conversion happening")
    def test_invalid_char(self):
        pass


class TestUnicodePptx(BaseTestCase, TestUnicodeBase):
    ext = "pptx"

    # A binary file is passed and text is not de/encoded.
    @unittest.skipIf(1, "no conversion happening")
    def test_invalid_char(self):
        pass


class TestUnicodePdf(BaseTestCase, TestUnicodeBase):
    ext = "pdf"


class TestUnicodePng(BaseTestCase, TestUnicodeBase):
    ext = "png"

    def compare(self, content_s, fulltext_s):
        pass

    @unittest.skipIf(1, "not compatible")
    def test_invalid_char(self):
        pass


class TestUnicodeJson(BaseTestCase, TestUnicodeBase):
    ext = "json"


class TestUnicodeDocx(BaseTestCase, TestUnicodeBase):
    ext = "docx"

    # Underlying lib doesn't allow to specify an encoding.
    @unittest.skipIf(1, "not compatible")
    def test_invalid_char(self):
        pass


class TestUnicodeEml(BaseTestCase, TestUnicodeBase):
    ext = "eml"


class TestUnicodeMbox(BaseTestCase, TestUnicodeBase):
    ext = "mbox"


# ===================================================================
# --- Test titles
# ===================================================================


class TestTitle(BaseTestCase):

    def test_html(self):
        fname = pathjoin(HERE, "files/others/title.html")
        self.assertEqual(
            fulltext.get_with_title(fname)[1], "Lorem ipsum")

    @unittest.skipIf(WINDOWS, "not supported on Windows")
    def test_pdf(self):
        fname = pathjoin(HERE, "files/others/test.pdf")
        self.assertEqual(
            fulltext.get_with_title(fname)[1], "This is a test PDF file")

    def test_odt(self):
        fname = pathjoin(HERE, "files/others/pretty-ones.odt")
        self.assertEqual(
            fulltext.get_with_title(fname)[1], "PRETTY ONES")

    @unittest.skipIf(WINDOWS, "not supported on Windows")
    def test_doc(self):
        fname = pathjoin(HERE, "files/others/hello-world.doc")
        fulltext.get_with_title(fname)
        self.assertEqual(
            fulltext.get_with_title(fname)[1], 'Lab 1: Hello World')

    def test_docx(self):
        fname = pathjoin(HERE, "files/others/hello-world.docx")
        self.assertEqual(
            fulltext.get_with_title(fname)[1], 'MPI example')

    @unittest.skipIf(TRAVIS, "fails on travis")
    def test_epub(self):
        fname = pathjoin(HERE, "files/others/jquery.epub")
        self.assertEqual(
            fulltext.get_with_title(fname)[1], 'JQuery Hello World')

    def test_pptx(self):
        fname = pathjoin(HERE, "files/others/test.pptx")
        self.assertEqual(
            fulltext.get_with_title(fname)[1], 'lorem ipsum')

    @unittest.skipIf(WINDOWS, "not supported on Windows")
    def test_ps(self):
        fname = pathjoin(HERE, "files/others/lecture.ps")
        self.assertEqual(
            fulltext.get_with_title(fname)[1], 'Hey there')

    @unittest.skipIf(WINDOWS, "not supported on Windows")
    def test_rtf(self):
        fname = pathjoin(HERE, "files/others/test.rtf")
        self.assertEqual(
            fulltext.get_with_title(fname)[1], 'hello there')

    def test_xls(self):
        fname = pathjoin(HERE, "files/others/test.xls")
        self.assertEqual(
            fulltext.get_with_title(fname)[1], 'hey there')

    def test_xlsx(self):
        fname = pathjoin(HERE, "files/others/test.xlsx")
        self.assertEqual(
            fulltext.get_with_title(fname)[1], 'yo man!')


# ===================================================================
# --- Test magic from file ext
# ===================================================================


class _BaseExtTests(object):

    def magic_from_file(self, fname):
        raise NotImplementedError("must be implemented in subclass")

    def doit(self, basename, mime):
        fname = pathjoin(HERE, "files", basename)
        magic_mime = self.magic_from_file(fname)
        self.assertEqual(magic_mime, mime)

    def test_csv(self):
        self.doit("test.csv", "text/csv")

    def test_doc(self):
        self.doit("test.doc", "application/msword")

    def test_docx(self):
        self.doit(
            "test.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document")  # NOQA

    def test_eml(self):
        self.doit("test.eml", "message/rfc822")

    def test_epub(self):
        self.doit("test.epub", "application/epub+zip")

    def test_gz(self):
        self.doit("test.gz", "application/gzip")

    def test_html(self):
        self.doit("test.html", "text/xhtml")

    def test_hwp(self):
        self.doit("test.hwp", "application/x-hwp")

    def test_json(self):
        self.doit("test.json", "application/json")

    def test_mbox(self):
        self.doit("test.mbox", "application/mbox")

    def test_ods(self):
        self.doit("test.ods", "application/vnd.oasis.opendocument.spreadsheet")

    def test_odt(self):
        self.doit("test.ods", "application/vnd.oasis.opendocument.spreadsheet")

    def test_pptx(self):
        self.doit(
            "others/test.pptx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation")  # NOQA

    def test_pdf(self):
        self.doit("test.pdf", "application/pdf")

    def test_psv(self):
        self.doit("test.psv", "text/csv")

    def test_rar(self):
        self.doit("test.rar", "application/x-rar-compressed")

    def test_rtf(self):
        self.doit("test.rtf", "application/rtf")

    def test_tsv(self):
        self.doit("test.tsv", "text/csv")

    def test_xls(self):
        self.doit("test.xls", "application/vnd.ms-excel")

    def test_xlsx(self):
        self.doit(
            "test.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")  # NOQA

    def test_xml(self):
        self.doit("test.xml", "application/x-xml")

    def test_zip(self):
        self.doit("test.zip", "application/zip")


@unittest.skipIf(WINDOWS, "libmagic not available on Windows")
class TestMagicFromFileExt(BaseTestCase, _BaseExtTests):

    def magic_from_file(self, fname):
        magic = MagicWrapper()
        return magic.from_file(fname, mime=True)


class TestPureMagicFromFileExt(BaseTestCase, _BaseExtTests):

    def magic_from_file(self, fname):
        magic = PuremagicWrapper()
        return magic.from_file(fname, mime=True)


# ===================================================================
# --- Test magic from file content
# ===================================================================


class _BaseFromFileContentTests(object):

    def magic_from_buffer(self, fname):
        raise NotImplementedError("must be implemented in subclass")

    def doit(self, basename, mime):
        fname = pathjoin(HERE, "files", basename)
        with open(fname, "rb") as f:
            chunk = f.read(2048)
        magic_mime = self.magic_from_buffer(chunk)
        self.assertEqual(magic_mime, mime)

    def test_csv(self):
        self.doit("test.csv", "text/plain")

    def test_doc(self):
        self.doit("test.doc", "application/CDFV2-unknown")

    def test_docx(self):
        self.doit(
            "test.docx", "application/zip")  # NOQA

    def test_eml(self):
        self.doit("test.eml", "text/plain")

    def test_epub(self):
        self.doit("test.epub", "application/epub+zip")

    def test_gz(self):
        self.doit("test.gz", "application/gzip")

    def test_html(self):
        self.doit("test.html", "text/html")

    def test_hwp(self):
        self.doit("test.hwp", "application/CDFV2-unknown")

    def test_json(self):
        self.doit("test.json", "text/plain")

    def test_mbox(self):
        self.doit("test.mbox", "text/plain")

    def test_ods(self):
        self.doit("test.ods", "application/vnd.oasis.opendocument.spreadsheet")

    def test_odt(self):
        self.doit("test.ods", "application/vnd.oasis.opendocument.spreadsheet")

    def test_pptx(self):
        self.doit(
            "others/test.pptx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation")  # NOQA

    def test_pdf(self):
        self.doit("test.pdf", "application/pdf")

    def test_psv(self):
        self.doit("test.psv", "text/plain")

    def test_rar(self):
        self.doit("test.rar", "application/x-rar")

    def test_rtf(self):
        self.doit("test.rtf", "text/rtf")

    def test_tsv(self):
        self.doit("test.tsv", "text/plain")

    def test_xls(self):
        self.doit("test.xls", "application/CDFV2-unknown")

    def test_xlsx(self):
        self.doit("test.xlsx", "application/octet-stream")

    def test_xml(self):
        self.doit("test.xml", "application/xml")

    def test_zip(self):
        self.doit("test.zip", "application/zip")


@unittest.skipIf(WINDOWS, "libmagic not available on Windows")
class TestMagicFromFileContent(BaseTestCase, _BaseFromFileContentTests):

    def magic_from_buffer(self, buffer):
        magic = MagicWrapper()
        return magic.from_buffer(buffer, mime=True)


# class TestPuremagicFromFileContent(BaseTestCase, _BaseFromFileContentTests):

#     def magic_from_buffer(self, buffer):
#         magic = PuremagicWrapper()
#         return magic.from_buffer(buffer, mime=True)


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
