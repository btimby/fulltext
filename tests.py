import unittest
import fulltext

def normalize_text(text):
    "Remove carriage returns etc."
    text = text.replace('\n', ' ')
    text = text.replace('  ', ' ')
    return text


TEST = normalize_text("""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc ipsum augue, iaculis quis auctor eu, adipiscing non est.
Nullam id sem diam, eget varius dui. Etiam sollicitudin sapien nec odio elementum sit amet luctus magna volutpat. Ut
commodo nulla neque. Aliquam erat volutpat. Integer et nunc augue. Pellentesque habitant morbi tristique senectus et
netus et malesuada fames ac turpis egestas. Quisque at enim nulla, vel tincidunt urna. Nam leo augue, elementum ut
viverra eget, scelerisque in purus. In arcu orci, porta nec aliquet quis, pretium a sem. In fermentum nisl id diam
luctus viverra. Nullam semper, metus at euismod vulputate, orci odio dignissim urna, quis iaculis neque lacus ut
tortor. Ut a justo non dolor venenatis accumsan. Proin dolor eros, aliquam id condimentum et, aliquam quis metus.
Vivamus eget purus diam.""")


class FullTextTest(unittest.TestCase):
    def test_missing_default(self):
        self.assertEqual(fulltext.get('non-existent-file.pdf', ''), '')

    def test_missing(self):
        self.assertRaises(fulltext.FullTextException, fulltext.get, 'non-existent-file.pdf')

    def test_unknown_default(self):
        self.assertEqual(fulltext.get('unknown-file.foobar', ''), '')

    def test_unknown(self):
        self.assertRaises(fulltext.FullTextException, fulltext.get, 'unknown-file.foobar')

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


def main():
    unittest.main()

if __name__ == '__main__':
    main()