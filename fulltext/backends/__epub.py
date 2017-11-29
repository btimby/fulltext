# To create a .epub file for test:
# run "sigil", open test.txt and save as epub.

from ebooklib import epub

from bs4 import BeautifulSoup

from six import StringIO


def _get_path(path, **kwargs):
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
