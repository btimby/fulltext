from __future__ import absolute_import

import csv

from six import StringIO


EXTENSIONS = ('csv', )


def readlines(f):
    for line in f.readlines():
        yield line.decode('utf8')


def _get_file(f, **kwargs):
    text = StringIO()
    for row in csv.reader(readlines(f), dialect='excel'):
        text.write(u' '.join(row))
        text.write(u'\n')
    return text.getvalue()
