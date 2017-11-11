import unittest
import fulltext

from fulltext.util import ShellError

from six import add_metaclass


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
	(
		u"Sherlock Holmes and Doctor Watson lived at 2211) Baker Street between 1881-1904,\n"
	),
	(
		u"Step back in time, and when you visit London, remember to visit the world's most\n"
		u"famous address!"
	)
)

FORMATS = (
    'txt', 'odt', 'docx', 'pptx', 'ods', 'xls', 'xlsx', 'html', 'xml', 'zip',
    'txt', 'rtf', 'test', 'hwp'
)


class FullText(unittest.TestCase):
    def test_missing_default(self):
        "Ensure a missing file returns default instead of exception."
        self.assertEqual(fulltext.get('non-existent-file.pdf', 'canary'),
                         'canary')

    def test_missing(self):
        "Ensure a missing file without a default raises an exception."
        # In this case we hit the pdf backend which runs a command, the
        # command fails because the file does not exist resulting in
        # ShellError.
        self.assertRaises(ShellError, fulltext.get, 'non-existent-file.pdf')

    def test_unknown_default(self):
        "Ensure unknown file type returns default instead of exception."
        self.assertEqual(fulltext.get('unknown-file.foobar', 'canary'),
                         'canary')

    def test_unknown(self):
        "Ensure unknown file type without a default raises an exception."
        # This is nearly a duplicate of test_missing, but in this case we hit
        # the default text backend, which attempts to open the file resulting
        # in an IOError.
        self.assertRaises(IOError, fulltext.get, 'unknown-file.foobar')

    def test_default_none(self):
        "Ensure None is a valid value to pass as default."
        self.assertEqual(fulltext.get('unknown-file.foobar', None), None)


class FullTextFilesMeta(type):
    "Tests various file types using disk file method."

    def __new__(cls, name, bases, attrs):
        for fmt in FORMATS:
            path = 'files/test.%s' % fmt
            attrs['test_%s_path' % fmt] = cls._test_path(path, fmt)
            attrs['test_%s_file' % fmt] = cls._test_file(path, fmt)
        return super(FullTextFilesMeta, cls).__new__(cls, name, bases, attrs)

    @classmethod
    def _test_file(cls, path, fmt):
        def inner(self):
            with open(path, 'rb') as f:
                text = fulltext.get(f, backend=fmt)
                self.assertEqual(text, TEXT)
        return inner

    @classmethod
    def _test_path(cls, path, fmt):
        def inner(self):
            text = fulltext.get(path, backend=fmt)
            self.assertEqual(text, TEXT)
        return inner


@add_metaclass(FullTextFilesMeta)
class FullTextFiles(unittest.TestCase):
    def assertStartsWith(self, prefix, body):
        self.assertTrue(body.startswith(prefix))

    def test_doc_file(self):
        "Antiword performs wrapping, so we need to allow newlines."
        with open('files/test.doc', 'rb') as f:
            text = fulltext.get(f, backend='doc')
            self.assertEqual(text, TEXT_WITH_NEWLINES)

    def test_doc_path(self):
        "Antiword performs wrapping, so we need to allow newlines."
        text = fulltext.get('files/test.doc', backend='doc')
        self.assertEqual(text, TEXT_WITH_NEWLINES)

    def test_old_doc_file(self):
        "Antiword does not support older Word documents."
        with open('files/test.old.doc', 'rb') as f:
            text = fulltext.get(f, backend='doc')
            self.assertStartsWith('eZ-Audit', text)

    def test_old_doc_path(self):
        "Antiword does not support older Word documents."
        text = fulltext.get('files/test.old.doc', backend='doc')
        self.assertStartsWith('eZ-Audit', text)

    def test_png_file(self):
        with open('files/test.png', 'rb') as f:
            text = fulltext.get(f)
            self.assertTrue(text.startswith (TEXT_FOR_OCR[0]))
            self.assertTrue(text.endswith (TEXT_FOR_OCR[1]))

    def test_png_path(self):        
        text = fulltext.get('files/test.png')
        self.assertTrue(text.startswith (TEXT_FOR_OCR[0]))
        self.assertTrue(text.endswith (TEXT_FOR_OCR[1]))


if __name__ == '__main__':
    unittest.main()
