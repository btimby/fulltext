import csv

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO


def _get_file(f, **kwargs):
    text = StringIO()
    for r in csv.reader(f.readlines(), dialect='excel'):
        text.write(' '.join(r))
    return text.getvalue()
