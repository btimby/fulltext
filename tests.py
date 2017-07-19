import os
import sys
import unittest
import fulltext

from functools import wraps

TEST = u"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc ipsum augue, iaculis quis auctor eu, adipiscing non est. " \
u"Nullam id sem diam, eget varius dui. Etiam sollicitudin sapien nec odio elementum sit amet luctus magna volutpat. Ut " \
u"commodo nulla neque. Aliquam erat volutpat. Integer et nunc augue. Pellentesque habitant morbi tristique senectus et " \
u"netus et malesuada fames ac turpis egestas. Quisque at enim nulla, vel tincidunt urna. Nam leo augue, elementum ut " \
u"viverra eget, scelerisque in purus. In arcu orci, porta nec aliquet quis, pretium a sem. In fermentum nisl id diam " \
u"luctus viverra. Nullam semper, metus at euismod vulputate, orci odio dignissim urna, quis iaculis neque lacus ut " \
u"tortor. Ut a justo non dolor venenatis accumsan. Proin dolor eros, aliquam id condimentum et, aliquam quis metus. " \
u"Vivamus eget purus diam."


def allow_missing_command(f):
    wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except fulltext.MissingCommandException:
            pass
    return wrapper


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


class FullTextFiles(unittest.TestCase):
    "Tests various file types using disk file method."

    @allow_missing_command
    def test_odt(self):
        self.assertEqual(fulltext.get('files/test.odt'), TEST)

    @allow_missing_command
    def test_ods(self):
        self.assertEqual(fulltext.get('files/test.ods'), TEST)

    @allow_missing_command
    def test_doc(self):
        self.assertEqual(fulltext.get('files/test.doc'), TEST)

    @allow_missing_command
    def test_pdf(self):
        self.assertEqual(fulltext.get('files/test.pdf'), TEST)

    @allow_missing_command
    def test_rtf(self):
        self.assertEqual(fulltext.get('files/test.rtf'), TEST)

    @allow_missing_command
    def test_xls(self):
        self.assertEqual(fulltext.get('files/test.xls'), TEST)

    @allow_missing_command
    def test_txt(self):
        self.assertEqual(fulltext.get('files/test.txt'), TEST)

    @allow_missing_command
    def test_zip(self):
        self.assertEqual(fulltext.get('files/test.zip'), TEST)


class FullTextFds(unittest.TestCase):
    "Tests various file types using file-like object method."

    @allow_missing_command
    def test_odt(self):
        self.assertEqual(fulltext.get(file('files/test.odt', 'r')), TEST)

    @allow_missing_command
    def test_ods(self):
        self.assertEqual(fulltext.get(file('files/test.ods', 'r')), TEST)

    @allow_missing_command
    def test_doc(self):
        self.assertEqual(fulltext.get(file('files/test.doc', 'r')), TEST)

    @allow_missing_command
    def test_pdf(self):
        self.assertEqual(fulltext.get(file('files/test.pdf', 'r')), TEST)

    @allow_missing_command
    def test_rtf(self):
        self.assertEqual(fulltext.get(file('files/test.rtf', 'r')), TEST)

    @allow_missing_command
    def test_xls(self):
        self.assertEqual(fulltext.get(file('files/test.xls', 'r')), TEST)

    @allow_missing_command
    def test_txt(self):
        self.assertEqual(fulltext.get(file('files/test.txt', 'r')), TEST)

    @allow_missing_command
    def test_zip(self):
        self.assertEqual(fulltext.get(file('files/test.zip', 'r')), TEST)


def main():
    unittest.main()


if __name__ == '__main__':
    main()