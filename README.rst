.. figure:: https://travis-ci.org/btimby/fulltext.png
   :alt: Travis CI Status
   :target: https://travis-ci.org/btimby/fulltext

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
* ``.mobi`` - Uses Python ``mobi`` module (from github).
* ``.ps`` - Uses ``/bin/pstotext`` CLI tool.
* ``.json`` - Uses ``json`` Python module.
* ``.eml`` - Uses ``email`` Python module.
* ``.mbox`` - Uses ``mailbox`` Python module.
* ``.bin`` - Uses Python stdlib modules to emulate ``strings`` CLI tool.

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

Custom backends
---------------

To write a new backend, you need to do two things. First, create a python
module that implements the interface that Fulltext expects. Second, register
the new backend against fulltext.

.. code:: python

    import fulltext

    def _get_file(f, **kwargs):
        # Extract text from a file-like object. This should be defined when
        # possible.
        pass

    def _get_path(path, **kwargs):
        # Extract text from a path. This should only be defined if it can be
        # done more efficiently than having Python open() and read() the file,
        # passing it to _get_file().
        pass

    fulltext.register_backend(
        'application/x-rar-compressed',
        'path.to.this.module',
        ['.rar'])

If you only implement ``_get_file()`` Fulltext will open any paths and pass
them to that function. Therefore if possible, define at least this function. If
working with file-like objects is not possible and you only define
``_get_path()`` then Fulltext will save any file-like objects to a temporary
file and use that function. Sometimes it is advantageous to define both
functions in cases when you can do each efficiently.

If you have questions about writing a backend, see the `./backends/`_ directory
for some examples.
