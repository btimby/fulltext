import zipfile
import xml.etree.ElementTree as ET

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO


def _qn(ns):
    nsmap = {
        'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
    }
    one, _, two = ns.partition(':')
    return '{{{}}}{}'.format(nsmap[one], two)


def _to_string(text, elem):
    if elem.text is not None:
        text.write(unicode(elem.text, 'utf8'))
    for c in elem:
        if c.tag == _qn('text:tab'):
            text.write(' ')
        elif c.tag == _qn('text:s'):
            text.write(' ')
            if c.tail is not None:
                text.write(c.tail)
        else:
            _to_string(text, c)
    text.write(u'\n')


def _get_file(f, **kwargs):
    text = StringIO()
    z = zipfile.ZipFile(f, 'r')
    xml = ET.fromstring(z.read('content.xml'))

    for c in xml.iter():
        if c.tag in (_qn('text:p'), _qn('text:h')):
            _to_string(text, c)

    return text.getvalue()


def _get_path(path, **kwargs):
    return _get_file(path, **kwargs)
