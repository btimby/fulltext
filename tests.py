#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest
import tempfile
try:
    from unittest import mock  # py3
except ImportError:
    import mock  # NOQA - requires "pip install mock"

import codecs
import difflib
import textwrap
import warnings

import fulltext
from fulltext.util import ShellError
from fulltext.util import which

from six import PY3
from six import BytesIO


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


# --- Utils


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

    def touch(self, fname, content=b""):
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
        self.assertRaises(ShellError, fulltext.get, 'non-existent-file.pdf')

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


class FullTextStripTestCase(BaseTestCase):
    """Test binary backend stripping."""

    def setUp(self):
        self.file = BytesIO()
        self.file.write(b'  Test leading and trailing spaces removal.  ')
        self.file.write(b'Test @$%* punctuation removal! ')
        self.file.write(b'Test    spaces     removal! ')
        self.file.seek(0)

    def test_text_strip(self):
        """Ensure that stripping works as expected."""
        stripped = fulltext.get(self.file, backend='bin')
        self.assertMultiLineEqual('Test leading and trailing spaces removal. '
                                  'Test punctuation removal! Test spaces '
                                  'removal!', stripped)


# --- Mixin tests


class PathAndFileTests(object):
    text = TEXT
    mime = None

    def test_file(self):
        path = 'files/test.%s' % self.ext
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
        path = 'files/test.%s' % self.ext
        if PY3:
            with self.assertRaises(AssertionError):
                self._handle_text(open(path, 'rt'))
        else:
            self._handle_text(open(path, 'rt'))

    def test_file_codecs(self):
        path = 'files/test.%s' % self.ext
        with self.assertRaises(AssertionError):
            self._handle_text(codecs.open(path, encoding='utf8'))

    def test_path(self):
        path = 'files/test.%s' % self.ext
        text = fulltext.get(path, mime=self.mime)
        self.assertMultiLineEqual(self.text, text)


class TxtTestCase(BaseTestCase, PathAndFileTests):
    ext = 'txt'


class OdtTestCase(BaseTestCase, PathAndFileTests):
    ext = 'odt'


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


class RtfTestCase(BaseTestCase, PathAndFileTests):
    ext = "rtf"


class CsvTestCase(BaseTestCase, PathAndFileTests):
    ext = "csv"
    mime = 'text/csv'
    text = TEXT.replace(',', '')


class TsvTestCase(BaseTestCase, PathAndFileTests):
    ext = "tsv"
    mime = 'text/tsv'


class PsvTestCase(BaseTestCase, PathAndFileTests):
    ext = "psv"
    mime = 'text/psv'


class PngTestCase(BaseTestCase, PathAndFileTests):
    ext = "png"


class EpubTestCase(BaseTestCase, PathAndFileTests):
    ext = "epub"


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

    # TODO: pdf backend can't handle file objects
    # def test_pdf(self):
    #     text = fulltext.get("files/gz/test.pdf.gz")
    #     self.assertMultiLineEqual(self.text, text)

    def test_csv(self):
        text = fulltext.get("files/gz/test.csv.gz")
        self.assertMultiLineEqual(self.text.replace(',', ''), text)

    def test_txt(self):
        text = fulltext.get("files/gz/test.txt.gz")
        self.assertMultiLineEqual(self.text, text)


# ---


class FilesTestCase(BaseTestCase):

    def test_old_doc_file(self):
        "Antiword does not support older Word documents."
        with open('files/test.old.doc', 'rb') as f:
            text = fulltext.get(f, backend='doc')
            self.assertStartsWith('eZ-Audit', text)
            self.assertIsInstance(text, u"".__class__)

    def test_old_doc_path(self):
        "Antiword does not support older Word documents."
        text = fulltext.get('files/test.old.doc', backend='doc')
        self.assertStartsWith('eZ-Audit', text)
        self.assertIsInstance(text, u"".__class__)


# --- Pickups


class TestPickups(BaseTestCase):
    """Make sure the right backend is called."""

    # --- by extension

    def test_by_ext(self):
        fname = self.touch('testfn.doc')
        with mock.patch('fulltext._get_path', return_value="") as m:
            fulltext.get(fname)
            mod = m.call_args[0][0]
            self.assertEqual(mod.__name__, 'fulltext.backends.__doc')

    def test_no_ext(self):
        # File with no extension == use bin backend.
        fname = self.touch('testfn')
        with mock.patch('fulltext._get_path', return_value="") as m:
            fulltext.get(fname)
            mod = m.call_args[0][0]
            self.assertEqual(mod.__name__, 'fulltext.backends.__bin')

    def test_unknown_ext(self):
        # File with unknown extension == use bin backend.
        fname = self.touch('testfn.unknown')
        with mock.patch('fulltext._get_path', return_value="") as m:
            fulltext.get(fname)
            mod = m.call_args[0][0]
            self.assertEqual(mod.__name__, 'fulltext.backends.__bin')

    # --- by mime opt

    def test_by_mime(self):
        fname = self.touch('testfn.doc')
        with mock.patch('fulltext._get_path', return_value="") as m:
            fulltext.get(fname, mime='application/vnd.ms-excel')
            mod = m.call_args[0][0]
            self.assertEqual(mod.__name__, 'fulltext.backends.__xlsx')

    def test_by_unknown_mime(self):
        fname = self.touch('testfn.doc')
        with mock.patch('fulltext._get_path', return_value="") as m:
            with warnings.catch_warnings(record=True) as ws:
                fulltext.get(fname, mime='application/yo!')
            assert ws
            mod = m.call_args[0][0]
            self.assertEqual(mod.__name__, 'fulltext.backends.__bin')

    # -- by name opt

    def test_by_name(self):
        fname = self.touch('testfn')
        with mock.patch('fulltext._get_path', return_value="") as m:
            fulltext.get(fname, name="woodstock.doc")
            mod = m.call_args[0][0]
            self.assertEqual(mod.__name__, 'fulltext.backends.__doc')

    def test_by_name_with_no_ext(self):
        # Assume bin backend is picked up.
        fname = self.touch("woodstock-no-ext")
        with mock.patch('fulltext._get_path', return_value="") as m:
            with warnings.catch_warnings(record=True) as ws:
                fulltext.get(fname, name=fname)
            assert ws
            mod = m.call_args[0][0]
            self.assertEqual(mod.__name__, 'fulltext.backends.__bin')

    # --- by backend opt

    def test_by_backend(self):
        # Assert file ext is ignored if backend opt is used.
        fname = self.touch('testfn.doc')
        with mock.patch('fulltext._get_path', return_value="") as m:
            fulltext.get(fname, backend='pdf')
            mod = m.call_args[0][0]
            self.assertEqual(mod.__name__, 'fulltext.backends.__pdf')

    def test_by_invalid_backend(self):
        # Assert file ext is ignored if backend opt is used.
        fname = self.touch('testfn.doc')
        with self.assertRaises(ValueError):
            fulltext.get(fname, backend='yoo')


# --- File objects


class TestFileObj(BaseTestCase):

    def test_returned_content(self):
        f = self.touch_fobj(content=b"hello world")
        ret = fulltext.get(f)
        self.assertEqual(ret, "hello world")

    def test_name_attr(self):
        # Make sure that fulltext attempts to determine file name
        # from "name" attr of the file obj.
        f = tempfile.NamedTemporaryFile(suffix='.pdf')
        with mock.patch('fulltext._get_file', return_value="") as m:
            fulltext.get(f)
            mod = m.call_args[0][0]
            self.assertEqual(mod.__name__, 'fulltext.backends.__pdf')

    def test_fobj_offset(self):
        # Make sure offset is unaltered after guessing mime type.
        f = self.touch_fobj(content=b"hello world")
        f.seek(0)
        mod = fulltext.backend_from_fobj(f)
        self.assertEqual(mod.__name__, 'fulltext.backends.__text')

    def test_no_magic(self):
        # Emulate a case where magic lib is not installed.
        f = self.touch_fobj(content=b"hello world")
        f.seek(0)
        with mock.patch("fulltext.magic", None):
            with warnings.catch_warnings(record=True) as ws:
                mod = fulltext.backend_from_fobj(f)
            self.assertIn("magic lib is not installed", str(ws[0].message))
            self.assertEqual(mod.__name__, 'fulltext.backends.__bin')


class TestGuessingFromFileContent(BaseTestCase):
    """Make sure that when file has no extension its type is guessed
    from its content.
    """

    def test_magic_is_installed(self):
        from fulltext.util import magic
        self.assertIsNotNone(magic)

    def test_pdf(self):
        fname = "file-noext"
        self.touch(fname, content=open('files/test.pdf', 'rb').read())
        with mock.patch('fulltext._get_path', return_value="") as m:
            fulltext.get(fname)
            mod = m.call_args[0][0]
            self.assertEqual(mod.__name__, 'fulltext.backends.__pdf')

    def test_html(self):
        fname = "file-noext"
        self.touch(fname, content=open('files/test.html', 'rb').read())
        with mock.patch('fulltext._get_path', return_value="") as m:
            fulltext.get(fname)
            mod = m.call_args[0][0]
            self.assertEqual(mod.__name__, 'fulltext.backends.__html')


class TestUtils(BaseTestCase):

    def test_is_file_path(self):
        assert fulltext.is_file_path('foo')
        assert fulltext.is_file_path(b'foo')
        assert not fulltext.is_file_path(open(__file__))


# --- Encodings


class TestEncodingGeneric(BaseTestCase):

    def test_global_vars(self):
        # Make sure the globla vars are taken into consideration and
        # passed to the underlying backends.
        encoding, errors = fulltext.ENCODING, fulltext.ENCODING_ERRORS
        fname = self.touch("file.txt", content=b"hello")
        try:
            fulltext.ENCODING = "foo"
            fulltext.ENCODING_ERRORS = "bar"
            with mock.patch('fulltext._get_path', return_value="") as m:
                fulltext.get(fname)
            self.assertEqual(m.call_args[1]['encoding'], 'foo')
            self.assertEqual(m.call_args[1]['encoding_errors'], 'bar')
        finally:
            fulltext.ENCODING = encoding
            fulltext.ENCODING_ERRORS = errors


class TestUnicodeBase(object):
    ext = None
    italian = "ciao bella àèìòù "
    japanese = "かいおうせい海王星"
    invalid = "helloworld"

    def compare(self, content_s, fulltext_s):
        if PY3:
            self.assertEqual(content_s, fulltext_s)
        else:
            # Don't test for equality on Python 2 because unicode
            # support is basically broken.
            pass

    def doit(self, fname, expected_txt):
        ret = fulltext.get(fname)
        self.compare(ret, expected_txt)

    def test_italian(self):
        self.doit("files/unicode/it.%s" % self.ext, self.italian)

    def test_japanese(self):
        self.doit("files/unicode/jp.%s" % self.ext, self.japanese)

    def test_invalid_char(self):
        fname = "files/unicode/invalid.%s" % self.ext
        if os.path.exists(fname):
            with self.assertRaises(UnicodeDecodeError):
                fulltext.get(fname)
            ret = fulltext.get(fname, encoding_errors="ignore")
            self.assertEqual(ret, self.invalid)
        #
        fname = "files/unicode/it.%s" % self.ext
        with self.assertRaises(UnicodeDecodeError):
            fulltext.get(fname, encoding='ascii')
        ret = fulltext.get(
            fname, encoding='ascii', encoding_errors="ignore")
        against = self.italian.replace("àèìòù", "").replace("  ", " ").strip()
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
class TestUnicodePs(BaseTestCase):

    def test_italian(self):
        fname = "files/unicode/it.ps"
        with self.assertRaises(UnicodeDecodeError):
            fulltext.get(fname)
        ret = fulltext.get(fname, encoding_errors="ignore")
        assert ret.startswith("ciao bella")  # the rest is garbage


class TestUnicodeHtml(BaseTestCase, TestUnicodeBase):
    ext = "html"


# backend uses `unrtf` CLI tool, which does not correctly
# handle unicode. Just make sure we don't crash if passed the
# error handler.
class TestUnicodeRtf(BaseTestCase):
    ext = "rtf"

    def test_italian(self):
        fname = "files/unicode/it.rtf"
        with self.assertRaises(UnicodeDecodeError):
            fulltext.get(fname)
        ret = fulltext.get(fname, encoding_errors="ignore")
        assert ret.startswith("ciao bella")  # the rest is garbage


class TestUnicodeDoc(BaseTestCase, TestUnicodeBase):
    ext = "doc"
    italian = ' '.join(["ciao bella àèìòù" for x in range(20)])
    japanese = ' '.join(["かいおうせい海王星" for x in range(30)])


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


if __name__ == '__main__':
    unittest.main(verbosity=2)
