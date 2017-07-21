import os
import sys
import unittest
import fulltext


TEXT = u"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc ipsum augue, iaculis quis auctor eu, adipiscing non est. " \
u"Nullam id sem diam, eget varius dui. Etiam sollicitudin sapien nec odio elementum sit amet luctus magna volutpat. Ut " \
u"commodo nulla neque. Aliquam erat volutpat. Integer et nunc augue. Pellentesque habitant morbi tristique senectus et " \
u"netus et malesuada fames ac turpis egestas. Quisque at enim nulla, vel tincidunt urna. Nam leo augue, elementum ut " \
u"viverra eget, scelerisque in purus. In arcu orci, porta nec aliquet quis, pretium a sem. In fermentum nisl id diam " \
u"luctus viverra. Nullam semper, metus at euismod vulputate, orci odio dignissim urna, quis iaculis neque lacus ut " \
u"tortor. Ut a justo non dolor venenatis accumsan. Proin dolor eros, aliquam id condimentum et, aliquam quis metus. " \
u"Vivamus eget purus diam."

FORMATS = (
    'txt', 'odt', 'doc', 'docx', 'pptx', 'ods', 'xls', 'xlsx', 'html',
    'xml', 'zip', 'txt', 'rtf', 'test',
)


class FullText(unittest.TestCase):
    def test_missing_default(self):
        "Ensures a missing file will return default value instead of exception."
        self.assertEqual(fulltext.get('non-existent-file.pdf', 'canary'), 'canary')

    def test_missing(self):
        "Ensures a missing file without a default raises an exception."
        self.assertRaises(Exception, fulltext.get, 'non-existent-file.pdf')

    def test_unknown_default(self):
        "Ensures an unknown file type will return default value instead of exception."
        self.assertEqual(fulltext.get('unknown-file.foobar', 'canary'), 'canary')

    def test_unknown(self):
        "Ensures an unknown file type without a default will raise an exception."
        self.assertRaises(Exception, fulltext.get, 'unknown-file.foobar')

    def test_default_none(self):
        "Ensures None is a valid value to pass as default."
        self.assertEqual(fulltext.get('unknown-file.foobar', None), None)


class TestFormats(type):
    "Tests various file types using disk file method."

    def __new__(mcs, name, bases, dict):

        def _test_file(path, format):
            def _test(self):
                with open(path, 'rb') as f:
                    text = fulltext.get(f, backend=format)
                    self.assertEqual(text, TEXT)
            return _test

        def _test_path(path, format):
            def _test(self):
                text = fulltext.get(path, backend=format)
                self.assertEqual(text, TEXT)
            return _test

        for f in FORMATS:
            path = 'files/test.%s' % f
            dict['test_%s_path' % f] = _test_path(path, f)
            dict['test_%s_file' % f] = _test_file(path, f)

        return type.__new__(mcs, name, bases, dict)


class FullTextFiles(unittest.TestCase):
    __metaclass__ = TestFormats


if __name__ == '__main__':
    unittest.main()
