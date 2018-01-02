.. figure:: https://travis-ci.org/btimby/fulltext.png
   :alt: Linux tests (Travis)
   :target: https://travis-ci.org/btimby/fulltext

.. image:: https://img.shields.io/appveyor/ci/btimby/fulltext/master.svg?maxAge=3600&label=Windows
    :alt: Windows tests (Appveyor)
    :target: https://ci.appveyor.com/project/btimby/fulltext

.. figure:: https://www.smartfile.com/assets/img/smartfile-logo-new.png
   :alt: SmartFile

.. _SmartFile: https://www.smartfile.com

A `SmartFile`_ Open Source project.

Introduction
------------

Fulltext extracts texts from various document formats. It can be used as the
first part of search indexing, document analysis etc.

Fulltext differs from other libraries in that it tries to use file data in the
form it is given. For most backends, a file-like object or path can be handled
directly, removing the need to write temporary files.

Fulltext uses native python libraries when possible and utilizes CLI tools
when necessary, for example, the following CLI tools are utilized.

* ``antiword`` - Legacy ``.doc`` (Word) format.
* ``unrtf`` - ``.rtf`` format.
* ``pdf2text`` (``apt install poppler-utils``) - ``.pdf`` format.
* ``pstotext`` (``apt install pstotext``) - ``.ps`` format.
* ``tesseract-ocr`` - image formats (OCR).
* ``abiword`` - office documents.

Supported formats
-----------------

* ``.csv`` - Uses Python ``csv`` module.
* ``.tsv`` (tab delimited) - Uses Python ``csv`` module.
* ``.psv`` (pipe delimited) - Uses Python ``csv`` module.
* ``.doc`` - Uses ``/bin/antiword`` CLI tool.
* ``.docx`` - Uses Python ``docx2txt`` module.
* ``.html`` - Uses Python ``BeautifulSoup`` module.
* ``.ods`` - Uses Python ``lxml``, ``zipfile`` modules.
* ``.odt`` - Uses Python ``lxml``, ``zipfile`` modules.
* ``.pdf`` - Uses ``/bin/pdf2text`` CLI tool.
* ``.rtf`` - Uses ``/bin/unrtf`` CLI tool.
* ``.text`` - Uses Python stdlib modules to extract text.
* ``.xls`` - Uses Python ``xlrd`` module.
* ``.xlsx`` - Uses Python ``xlrd`` module.
* ``.xml`` - Uses Python ``lxml`` module.
* ``.pptx`` - Uses Python ``pptx`` module
* ``.zip`` - Uses Python ``zipfile`` module.
* ``.gz`` - Uses Python ``gzip`` module.
* ``.jpg``, ``.jpeg``, ``.png``, ``.bmp``, ``.gif`` - Uses ``/usr/bin/tesseract`` CLI tool and ``pytesseract`` module.
* ``.hwp`` - Uses Python ``pyhwp`` module as CLI tool.
* ``.epub`` - Uses Python ``ebooklib`` module.
* ``.ps`` - Uses ``/bin/pstotext`` CLI tool.
* ``.json`` - Uses ``json`` Python module.
* ``.eml`` - Uses ``email`` Python module.
* ``.mbox`` - Uses ``mailbox`` Python module.
* ``.msg`` - Uses ``msg-extractor`` Python module (from github).
* ``.bin`` - Uses Python stdlib modules to emulate ``strings`` CLI tool.
* ``.rar`` - Uses ``rarfile`` module.

Supported title formats
-----------------------

Other than extracting text fulltext lib is able to determine title for certain
file extensions:

* ``.doc`` - Uses ``/bin/exiftool`` CLI tool.
* ``.docx`` - Uses ``/bin/exiftool`` CLI tool.
* ``.epub`` - Uses ``/bin/exiftool`` CLI tool.
* ``.html`` - Uses Python ``BeautifulSoup`` module.
* ``.odt`` - Uses ``/bin/exiftool`` CLI tool.
* ``.pdf`` - Uses ``/bin/pdfinfo`` CLI tool.
* ``.pptx`` - Uses ``/bin/pdfinfo`` CLI tool.
* ``.ps`` - Uses ``/bin/exiftool`` CLI tool.
* ``.rtf`` - Uses ``/bin/exiftool`` CLI tool.
* ``.xls`` - Uses ``/bin/exiftool`` CLI tool.
* ``.xlsx`` - Uses ``/bin/exiftool`` CLI tool.

Installing tools
----------------

Fulltext uses a number of pure Python libraries. Fulltext also uses the
command line tools: antiword, pdf2text and unrtf. To install the required
libraries and CLI tools, you can use your package manager.

.. code:: bash

    $ sudo yum install antiword abiword unrtf poppler-utils libjpeg-dev \
    tesseract-ocr pstotext

Or for debian-based systems:

.. code:: bash

    $ sudo apt-get install antiword abiword unrtf poppler-utils libjpeg-dev \
    pstotext

Usage
-----

Fulltext uses a simple dictionary-style interface. A single public function
``fulltext.get()`` is provided. This function takes an optional default
parameter which when supplied will supress errors and return that default if
text could not be extracted.

.. code:: python

    >>> import fulltext
    >>>
    >>> fulltext.get('does-not-exist.pdf', None)
    None
    >>> fulltext.get('exists.pdf', None)
    'Lorem ipsum...'

You can pass a file-like object or a path to ``.get()`` Fulltext will try to
do the right thing, using memory buffers or temp files depending on the
backend.

You should pass any file details you have available, such as the file name or
mime type. These will help fulltext select the correct backend. If you want to
specify the backend explicitly, use the backend keyword argument.

.. code:: python

    >>> with open('foo.pdf' 'rb') as f:
    ...     fulltext.get(f, name='foo.pdf', mime='application/pdf',
    ...                  backend='pdf')

Some backends accept additonal parameters. You can pass these using the
``kwargs`` key word argument.

.. code:: python

    >>> fulltext.get('foo.pdf', kwargs={'option': 'value'})

You can also get the title for certain file formats:

.. code:: python

    >>> fulltext.get_with_title('foo.pdf')
    ('file content', 'file title')

You can specify the encoding to use (defaults to `sys.getfilesystemencoding()`
+ `strict` error handler):


.. code:: python

    >>> fulltext.get('foo.pdf', encoding='latin1', encoding_errors='ignore')

Custom backends
---------------

To write a new backend, you need to do two things.
First, create a python module within a `Backend` class that implements the
interface that Fulltext expects.
Second, register the new backend against fulltext.

.. code:: python

    import fulltext
    from fulltext import BaseBackend


    fulltext.register_backend(
        'application/x-rar-compressed',
        'path.to.this.module',
        ['.rar'])


    class Backend(BaseBackend):

        def check(title):
            # This is invoked before `handle_` functions. In here you can
            # import third party deps or raise an exception if a CLI tool
            # is missing. Both conditions will be turned into a warning
            # on `get()` and bin backend will be used as fallback.
            pass

        def setup():
            # This is called before `handle_` functions.
            pass

        def teardown():
            # This is called after `handle_` functions, also in case of error.
            pass

        def handle_fobj(f, **kwargs):
            # Extract text from a file-like object. This should be defined when
            # possible.

            # These are the available instance attributes passed to `get()`
            # function.
            self.mime
            self.encoding
            self.encoding_errors
            self.kwargs

        def handle_path(path, **kwargs):
            # Extract text from a path. This should only be defined if it can be
            # done more efficiently than having Python open() and read() the file,
            # passing it to handle_fobj().
            pass

        def handle_title(file_or_path):
            # Extract title
            pass

If you only implement ``handle_fobj()`` Fulltext will open any paths and pass
them to that function. Therefore if possible, define at least this method. If
working with file-like objects is not possible and you only define
``handle_path()`` then Fulltext will save any file-like objects to a temporary
file and use that function. Sometimes it is advantageous to define both
functions in cases when you can do each efficiently.

If you have questions about writing a backend, see the `./backends/`_ directory
for some examples.
