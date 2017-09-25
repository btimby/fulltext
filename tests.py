import unittest
import fulltext

from six import add_metaclass


TEXT = u"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc ipsum" \
       u" augue, iaculis quis auctor eu, adipiscing non est. Nullam id sem " \
       u"diam, eget varius dui. Etiam sollicitudin sapien nec odio elementum" \
       u" sit amet luctus magna volutpat. Ut commodo nulla neque. Aliquam " \
       u"erat volutpat. Integer et nunc augue. Pellentesque habitant morbi " \
       u"tristique senectus et netus et malesuada fames ac turpis egestas. " \
       u"Quisque at enim nulla, vel tincidunt urna. Nam leo augue, elementum" \
       u" ut viverra eget, scelerisque in purus. In arcu orci, porta nec " \
       u"aliquet quis, pretium a sem. In fermentum nisl id diam luctus " \
       u"viverra. Nullam semper, metus at euismod vulputate, orci odio " \
       u"dignissim urna, quis iaculis neque lacus ut tortor. Ut a justo non " \
       u"dolor venenatis accumsan. Proin dolor eros, aliquam id condimentum " \
       u"et, aliquam quis metus. Vivamus eget purus diam."

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
    pass


if __name__ == '__main__':
    unittest.main()
