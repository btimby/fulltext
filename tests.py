import unittest
import fulltext

TEST = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc ipsum augue, iaculis quis auctor eu, adipiscing non est. " \
"Nullam id sem diam, eget varius dui. Etiam sollicitudin sapien nec odio elementum sit amet luctus magna volutpat. Ut " \
"commodo nulla neque. Aliquam erat volutpat. Integer et nunc augue. Pellentesque habitant morbi tristique senectus et " \
"netus et malesuada fames ac turpis egestas. Quisque at enim nulla, vel tincidunt urna. Nam leo augue, elementum ut " \
"viverra eget, scelerisque in purus. In arcu orci, porta nec aliquet quis, pretium a sem. In fermentum nisl id diam " \
"luctus viverra. Nullam semper, metus at euismod vulputate, orci odio dignissim urna, quis iaculis neque lacus ut " \
"tortor. Ut a justo non dolor venenatis accumsan. Proin dolor eros, aliquam id condimentum et, aliquam quis metus. " \
"Vivamus eget purus diam."


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
        self.assertEqual(fulltext.get(file('files/test.test', 'r')), TEST)

    def test_command(self):
        """Ensures that commands registered for a given type are executed by the `run_command` handler
        when that type is converted."""
        fulltext.add('application/test', '.test', fulltext.run_command, (('echo', TEST), ('echo', TEST), ))
        self.assertEqual(fulltext.get('files/test.test'), TEST)
        self.assertEqual(fulltext.get(file('files/test.test', 'r')), TEST)


class FullTextFiles(unittest.TestCase):
    "Tests various file types using disk file method."

    def test_odt(self):
        self.assertEqual(fulltext.get('files/test.odt'), TEST)

    def test_ods(self):
        self.assertEqual(fulltext.get('files/test.ods'), TEST)

    def test_doc(self):
        self.assertEqual(fulltext.get('files/test.doc'), TEST)

    def test_pdf(self):
        self.assertEqual(fulltext.get('files/test.pdf'), TEST)

    def test_rtf(self):
        self.assertEqual(fulltext.get('files/test.rtf'), TEST)

    def test_xls(self):
        self.assertEqual(fulltext.get('files/test.xls'), TEST)

    def test_txt(self):
        self.assertEqual(fulltext.get('files/test.txt'), TEST)

    def test_zip(self):
        self.assertEqual(fulltext.get('files/test.zip'), TEST)


class FullTextFds(unittest.TestCase):
    "Tests various file types using file-like object method."

    def test_odt(self):
        self.assertEqual(fulltext.get(file('files/test.odt', 'r')), TEST)

    def test_ods(self):
        self.assertEqual(fulltext.get(file('files/test.ods', 'r')), TEST)

    def test_doc(self):
        self.assertEqual(fulltext.get(file('files/test.doc', 'r')), TEST)

    def test_pdf(self):
        self.assertEqual(fulltext.get(file('files/test.pdf', 'r')), TEST)

    def test_rtf(self):
        self.assertEqual(fulltext.get(file('files/test.rtf', 'r')), TEST)

    def test_xls(self):
        self.assertEqual(fulltext.get(file('files/test.xls', 'r')), TEST)

    def test_txt(self):
        self.assertEqual(fulltext.get(file('files/test.txt', 'r')), TEST)

    def test_zip(self):
        self.assertEqual(fulltext.get(file('files/test.zip', 'r')), TEST)


def main():
    unittest.main()

if __name__ == '__main__':
    main()