import os
import sys
import unittest
import fulltext

from functools import wraps

TEST = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc ipsum augue, iaculis quis auctor eu, adipiscing non est. " \
"Nullam id sem diam, eget varius dui. Etiam sollicitudin sapien nec odio elementum sit amet luctus magna volutpat. Ut " \
"commodo nulla neque. Aliquam erat volutpat. Integer et nunc augue. Pellentesque habitant morbi tristique senectus et " \
"netus et malesuada fames ac turpis egestas. Quisque at enim nulla, vel tincidunt urna. Nam leo augue, elementum ut " \
"viverra eget, scelerisque in purus. In arcu orci, porta nec aliquet quis, pretium a sem. In fermentum nisl id diam " \
"luctus viverra. Nullam semper, metus at euismod vulputate, orci odio dignissim urna, quis iaculis neque lacus ut " \
"tortor. Ut a justo non dolor venenatis accumsan. Proin dolor eros, aliquam id condimentum et, aliquam quis metus. " \
"Vivamus eget purus diam."

ENC_TEST = u"Lorem ipsum dolor sit amet, cons\xe9ct\xeatur adipiscing elit. Nunc ipsum augue, iaculis quis " \
u"auctor eu, adipiscing non est. Nullam id sem diam, \xe9g\xeat varius dui. Etiam sollicitudin sapien nec odio " \
u"\xe9lem\xeantum sit amet luctus magna volutpat. Ut commodo nulla n\xe9qu\xea. Aliquam erat volutpat. " \
u"Int\xe9g\xear et nunc augue. P\xe9llent\xeasque habitant morbi tristique s\xe9n\xeactus et netus et malesuada " \
u"fames ac turpis \xe9g\xeastas. Quisque at enim nulla, vel tincidunt urna. Nam leo augue, \xe9lem\xeantum ut " \
u"viverra \xe9g\xeat, sc\xe9l\xearisque in purus. In arcu orci, porta nec aliquet quis, pretium a sem. In " \
u"f\xe9rm\xeantum nisl id diam luctus viverra. Nullam s\xe9mp\xear, metus at euismod vulputate, orci odio " \
u"dignissim urna, quis iaculis neque lacus ut tortor. Ut a justo non dolor v\xe9n\xeanatis accumsan. Proin dolor " \
u"eros, aliquam id condimentum et, aliquam quis metus. Vivamus \xe9g\xeat purus diam."

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
        self.assertRaises(fulltext.FullTextException, fulltext.get, 'non-existent-file.pdf')

    def test_unknown_default(self):
        "Ensures an unknown file type will return default value instead of exception."
        self.assertEqual(fulltext.get('unknown-file.foobar', 'canary'), 'canary')

    def test_unknown(self):
        "Ensures an unknown file type without a default will raise an exception."
        self.assertRaises(fulltext.FullTextException, fulltext.get, 'unknown-file.foobar')

    def test_default_none(self):
        "Ensures None is a valid value to pass as default."
        self.assertEqual(fulltext.get('unknown-file.foobar', None), None)

    def test_handler(self):
        "Ensures that a handler registered for a given type is executed when that type is converted."
        def test_handler(f, type):
            return TEST
        fulltext.add('application/test', '.test', test_handler)
        self.assertEqual(fulltext.get('files/test.test'), TEST)
        with open('files/test.test', 'r') as fo:
            self.assertEqual(fulltext.get(fo), TEST)

    def test_command(self):
        """Ensures that commands registered for a given type are executed by the `run_command` handler
        when that type is converted."""
        fulltext.add('application/test', '.test', fulltext.run_command, (('echo', TEST), ('echo', TEST), ))
        self.assertEqual(fulltext.get('files/test.test'), TEST)
        with open('files/test.test', 'r') as fo:
            self.assertEqual(fulltext.get(fo), TEST)


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
        with open('files/test.odt', 'rb') as fo:
            self.assertEqual(fulltext.get(fo), TEST)

    @allow_missing_command
    def test_ods(self):
        with open('files/test.ods', 'rb') as fo:
            self.assertEqual(fulltext.get(fo), TEST)

    @allow_missing_command
    def test_doc(self):
        with open('files/test.doc', 'rb') as fo:
            self.assertEqual(fulltext.get(fo), TEST)

    @allow_missing_command
    def test_pdf(self):
        with open('files/test.pdf', 'rb') as fo:
            self.assertEqual(fulltext.get(fo), TEST)

    @allow_missing_command
    def test_rtf(self):
        with open('files/test.rtf', 'rb') as fo:
            self.assertEqual(fulltext.get(fo), TEST)

    @allow_missing_command
    def test_xls(self):
        with open('files/test.xls', 'rb') as fo:
            self.assertEqual(fulltext.get(fo), TEST)

    @allow_missing_command
    def test_txt(self):
        with open('files/test.txt', 'r') as fo:
            self.assertEqual(fulltext.get(fo), TEST)

    @allow_missing_command
    def test_zip(self):
        with open('files/test.zip', 'rb') as fo:
            self.assertEqual(fulltext.get(fo), TEST)

class FullTextEncodedFiles(unittest.TestCase):
    "Tests various file types using disk file method."

    @allow_missing_command
    def test_txt(self):
        self.assertEqual(fulltext.get('files/test_enc.txt'), ENC_TEST)

    @allow_missing_command
    def test_doc(self):
        self.assertEqual(fulltext.get('files/test_enc.doc'), ENC_TEST)


class FullTextEncodedFds(unittest.TestCase):
    "Tests various file types using file-like object method."

    @allow_missing_command
    def test_txt(self):
        with open('files/test_enc.txt', 'r') as fo:
            self.assertEqual(fulltext.get(fo), ENC_TEST)

    @allow_missing_command
    def test_doc(self):
        with open('files/test_enc.doc', 'rb') as fo:
            self.assertEqual(fulltext.get(fo), ENC_TEST)


class FullTextCheck(unittest.TestCase):
    "Test the check function."

    def test_success(self):
        "At least verify the function executes without an error."
        # The output can be ignored
        stdout = sys.stdout
        with open(os.devnull, 'w') as stdout_fo:
            try:
                sys.stdout = stdout_fo
            except:
                # We tried... not core to the test though.
                pass
            try:
                fulltext.check()
            except Exception as e:
                self.fail(str(e))
            finally:
                sys.stdout = stdout


def main():
    unittest.main()


if __name__ == '__main__':
    main()
