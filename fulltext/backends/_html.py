from __future__ import absolute_import

import re

from bs4 import BeautifulSoup

from fulltext.util import StringIO


EXTENSIONS = ('htm', 'html')


def _get_file(f, **kwargs):
    text = StringIO()
    bs = BeautifulSoup(f, 'lxml')

