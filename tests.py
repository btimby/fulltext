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
        self.assertEqual(fulltext.get('non-existent-file.pdf', ''), '')

    def test_missing(self):
        self.assertRaises(fulltext.FullTextException, fulltext.get, 'non-existent-file.pdf')

    def test_unknown_default(self):
        self.assertEqual(fulltext.get('unknown-file.foobar', ''), '')

    def test_unknown(self):
        self.assertRaises(fulltext.FullTextException, fulltext.get, 'unknown-file.foobar')

class FullTextFiles(unittest.TestCase):
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