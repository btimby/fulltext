# To create a .epub file for test:
# run "sigil", open test.txt and save as epub.

from ebooklib import epub

from bs4 import BeautifulSoup
from six import StringIO

from fulltext.util import BaseBackend
from fulltext.util import assert_cmd_exists
from fulltext.util import exiftool_title


class Backend(BaseBackend):

    def check(self, title):
        if title:
            assert_cmd_exists('exiftool')

    def handle_path(self, path):
        text, book = StringIO(), epub.read_epub(path)

        for id, _ in book.spine:
            item = book.get_item_with_id(id)
            soup = BeautifulSoup(item.content, 'lxml')
            for child in soup.find_all(
                ['title', 'p', 'div', 'h1', 'h2', 'h3', 'h4']
            ):
                text.write(child.text)
                text.write(u'\n')

        return text.getvalue()

    def handle_title(self, f):
        return exiftool_title(f, self.encoding, self.encoding_errors)
