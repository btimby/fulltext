import unittest
import fulltext

from fulltext.util import ShellError
from fulltext.util import which


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

TEXT_FOR_OCR = (
    u"Sherlock Holmes and Doctor Watson lived at 2211) Baker Street " \
    u"between 1881-1904,",
    u"Step back in time, and when you visit London, remember to visit " \
    u"the world's most famous address!"
)


class BaseTestCase(unittest.TestCase):
    def assertStartsWith(self, prefix, body):
        if not body.startswith(prefix):
            msg = '"%s" != "%s"' % (body[:len(prefix)], prefix)
            raise AssertionError(msg)

    def assertEndsWith(self, postfix, body):
        if not body.endswith(postfix):
            msg = '"%s" != "%s"' % (body[0 - len(postfix):], postfix)
            raise AssertionError(msg)


class FullText(BaseTestCase):
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


class TestPathAndFile(object):

    def test_file(self):
        path = 'files/test.%s' % self.ext
        with open(path, 'rb') as f:
            text = fulltext.get(f, backend=self.ext)
            self.assertSequenceEqual(TEXT, text)

    def test_path(self):
        path = 'files/test.%s' % self.ext
        text = fulltext.get(path, backend=self.ext)
        self.assertSequenceEqual(TEXT, text)


class TestTxt(BaseTestCase, TestPathAndFile):
    ext = "txt"


class TestOdt(BaseTestCase, TestPathAndFile):
    ext = "odt"


class TestDoc(BaseTestCase, TestPathAndFile):
    ext = "doc"


class TestDocx(BaseTestCase, TestPathAndFile):
    ext = "docx"


class TestOds(BaseTestCase, TestPathAndFile):
    ext = "ods"


class TestXls(BaseTestCase, TestPathAndFile):
    ext = "xls"


class TestXlsx(BaseTestCase, TestPathAndFile):
    ext = "xlsx"


class TestHtml(BaseTestCase, TestPathAndFile):
    ext = "html"


class TestXml(BaseTestCase, TestPathAndFile):
    ext = "xml"


class TestZip(BaseTestCase, TestPathAndFile):
    ext = "zip"


class TestRtf(BaseTestCase, TestPathAndFile):
    ext = "rtf"


class TestTest(BaseTestCase, TestPathAndFile):
    ext = "test"


@unittest.skipIf(not which('pyhwp'), "pyhwp not installed")
class TestHwp(BaseTestCase, TestPathAndFile):
    ext = "hwp"


class FullTextFiles(BaseTestCase):
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

    def test_png_file(self):
        with open('files/test.png', 'rb') as f:
            text = fulltext.get(f)
            self.assertStartsWith(TEXT_FOR_OCR[0], text)
            self.assertEndsWith(TEXT_FOR_OCR[1], text)
            self.assertIsInstance(text, u"".__class__)

    def test_png_path(self):
        text = fulltext.get('files/test.png')
        self.assertStartsWith(TEXT_FOR_OCR[0], text)
        self.assertEndsWith(TEXT_FOR_OCR[1], text)
        self.assertIsInstance(text, u"".__class__)

    def test_csv_file(self):
        with open('files/test.csv', 'rb') as f:
            text = fulltext.get(f)
            self.assertStartsWith('Lorem', text)
            self.assertIsInstance(text, u"".__class__)

    def test_csv_path(self):
        text = fulltext.get('files/test.csv')
        self.assertStartsWith('Lorem', text)
        self.assertIsInstance(text, u"".__class__)


if __name__ == '__main__':
    unittest.main(verbosity=2)
