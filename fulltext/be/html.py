import re

from bs4 import BeautifulSoup

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO


def _get_file(f, **kwargs):
    text = StringIO()
    bs = BeautifulSoup(f, 'lxml')

