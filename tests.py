import os
import unittest
try:
    from unittest import mock  # py3
except ImportError:
    import mock  # NOQA - requires "pip install mock"

import codecs
import difflib
import textwrap

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


class BaseTestCase(unittest.TestCase):
    """Base TestCase Class."""

    def assertMultiLineEqual(self, a, b, msg=None):
        """A useful assertion for troubleshooting."""
        # Check if two blocks of text are equal.
        if a == b:
            return

        if msg is None:
            # If not the same, and no msg provided, create a user-friendly
            # diff message.
            a = textwrap.wrap(a)
            b = textwrap.wrap(b)
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


class PathAndFileTests(object):
    text = TEXT

    def test_file(self):
        path = 'files/test.%s' % self.ext
        with open(path, 'rb') as f:
            text = fulltext.get(f, backend=self.ext)
            self.assertMultiLineEqual(self.text, text)

    def _handle_text(self, f):
        """Main body of both 'text mode' tests."""
        try:
            text = fulltext.get(f, backend=self.ext)
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
        text = fulltext.get(path, backend=self.ext)
        self.assertMultiLineEqual(self.text, text)


class TxtTestCase(BaseTestCase, PathAndFileTests):
    ext = "txt"


class OdtTestCase(BaseTestCase, PathAndFileTests):
    ext = "odt"


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


class TestCase(BaseTestCase, PathAndFileTests):
    ext = "test"


class CsvTestCase(BaseTestCase, PathAndFileTests):
    ext = "csv"
    text = TEXT.replace(',', '')


class PngTestCase(BaseTestCase, PathAndFileTests):
    ext = "png"


@unittest.skipIf(not which('pyhwp'), "pyhwp not installed")
class HwpTestCase(BaseTestCase, PathAndFileTests):
    ext = "hwp"


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


class TestPickups(BaseTestCase):
    """Make sure the right backend is called."""

    def touch(self, fname, content=""):
        with open(fname, 'wt') as f:
            if content:
                f.write(content)
        self.addCleanup(os.remove, fname)

    def test_by_ext(self):
        fname = 'testfn.doc'
        self.touch(fname)
        with mock.patch('fulltext._get_path', return_value="") as m:
            fulltext.get(fname)
            mod = m.call_args[0][0]
            self.assertEqual(mod.__name__, 'fulltext.backends.__doc')

    def test_no_ext(self):
        # File with no extension == use bin backend.
        fname = 'testfn'
        self.touch(fname)
        with mock.patch('fulltext._get_path', return_value="") as m:
            fulltext.get(fname)
            mod = m.call_args[0][0]
            self.assertEqual(mod.__name__, 'fulltext.backends.__bin')

    def test_unknown_ext(self):
        # File with unknown extension == use bin backend.
        fname = 'testfn.unknown'
        self.touch(fname)
        with mock.patch('fulltext._get_path', return_value="") as m:
            fulltext.get(fname)
            mod = m.call_args[0][0]
            self.assertEqual(mod.__name__, 'fulltext.backends.__bin')

    def test_backend_opt(self):
        # Assert file ext is ignored if backend opt is used.
        fname = 'testfn.doc'
        self.touch(fname)
        with mock.patch('fulltext._get_path', return_value="") as m:
            fulltext.get(fname, backend='pdf')
            mod = m.call_args[0][0]
            self.assertEqual(mod.__name__, 'fulltext.backends.__pdf')


if __name__ == '__main__':
    unittest.main(verbosity=2)
