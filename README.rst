.. figure:: https://travis-ci.org/btimby/fulltext.png
   :alt: Linux tests (Travis)
   :target: https://travis-ci.org/btimby/fulltext

.. image:: https://img.shields.io/appveyor/ci/btimby/fulltext/master.svg?maxAge=3600&label=Windows
    :target: https://ci.appveyor.com/project/btimby/fulltext
    :alt: Windows tests (Appveyor)

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

Fulltext uses native python libraries when possible and utilizes third party
Python libraries and CLI tools when necessary, for example, the following (but
not only) CLI tools are utilized.

* ``antiword`` - Legacy ``.doc`` (Word) format.
* ``unrtf`` - ``.rtf`` format.
* ``pdf2text`` (``apt install poppler-utils``) - ``.pdf`` format.
* ``pstotext`` (``apt install pstotext``) - ``.ps`` format.
* ``tesseract-ocr`` - image formats (OCR).
* ``abiword`` - office documents.

Supported formats
-----------------

+-----------+-------------------------------------+----------------------------------------------+
| Extension | Linux                               | Windows                                      |
+===========+=====================================+==============================================+
| ``bin``   | python stdlib                       | python stdlib                                |
+-----------+-------------------------------------+----------------------------------------------+
| ``bmp``   | tesseract CLI and pytesserac module |                                              |
+-----------+-------------------------------------+----------------------------------------------+
| ``csv``   | python ``csv`` module               | python ``csv`` module                        |
+-----------+-------------------------------------+----------------------------------------------+
| ``doc``   | ``antiword`` CLI tool               |                                              |
+-----------+-------------------------------------+----------------------------------------------+
| ``docx``  | ``docx2txt`` module                 | ``docx2txt`` module                          |
+-----------+-------------------------------------+----------------------------------------------+
| ``eml``   | ``email`` module                    | ``email`` module                             |
+-----------+-------------------------------------+----------------------------------------------+
| ``epub``  | ``ebooklib`` module                 | ``ebooklib`` module                          |
+-----------+-------------------------------------+----------------------------------------------+
| ``gif``   | tesseract CLI and pytesserac module |                                              |
+-----------+-------------------------------------+----------------------------------------------+
| ``gz``    | python ``gzip`` module              | python ``gzip`` module                       |
+-----------+-------------------------------------+----------------------------------------------+
| ``html``  | ``BeautifulSoup`` module            | ``BeautifulSoup`` module                     |
+-----------+-------------------------------------+----------------------------------------------+
| ``hwp``   | ``pyhwp`` module as CLI tool        |                                              |
+-----------+-------------------------------------+----------------------------------------------+
| ``jpg``   | tesseract CLI and pytesserac module |                                              |
+-----------+-------------------------------------+----------------------------------------------+
| ``json``  | ``json`` module                     | ``json`` module                              |
+-----------+-------------------------------------+----------------------------------------------+
| ``mbox``  | ``mailbox`` module                  | ``mailbox`` modul                            |
+-----------+-------------------------------------+----------------------------------------------+
| ``msg``   | ``msg-extractor`` module            |                                              |
+-----------+-------------------------------------+----------------------------------------------+
| ``ods``   | ``lxml``, ``zipfile`` modules       | ``lxml``, ``zipfile`` modules                |
+-----------+-------------------------------------+----------------------------------------------+
| ``odt``   | ``lxml``, ``zipfile`` modules       | ``lxml``, ``zipfile`` modules                |
+-----------+-------------------------------------+----------------------------------------------+
| ``pdf``   | ``pdf2text`` CLI tool               | ``pdf2text`` CLI tool                        |
+-----------+-------------------------------------+----------------------------------------------+
| ``png``   | tesseract CLI and pytesserac module |                                              |
+-----------+-------------------------------------+----------------------------------------------+
| ``pptx``  | ``pptx`` module                     |                                              |
+-----------+-------------------------------------+----------------------------------------------+
| ``ps``    | ``pstotext`` CLI tool               |                                              |
+-----------+-------------------------------------+----------------------------------------------+
| ``psv``   | python ``csv`` module               | python ``csv`` module                        |
+-----------+-------------------------------------+----------------------------------------------+
| ``rar``   | ``rarfile`` module                  | ``rarfile`` module                           |
+-----------+-------------------------------------+----------------------------------------------+
| ``rtf``   | ``unrtf`` CLI tool                  | ``unrtf`` CLI tool                           |
+-----------+-------------------------------------+----------------------------------------------+
| ``text``  | python stdlib                       | python stdlib                                |
+-----------+-------------------------------------+----------------------------------------------+
| ``tsv``   | python ``csv`` module               | python ``csv`` module                        |
+-----------+-------------------------------------+----------------------------------------------+
| ``xls``   | ``xlrd`` module                     | ``xlrd`` module                              |
+-----------+-------------------------------------+----------------------------------------------+
| ``xlsx``  | ``xlrd`` module                     | ``xlrd`` module                              |
+-----------+-------------------------------------+----------------------------------------------+
| ``xml``   | ``lxml`` module                     | ``lxml`` module                              |
+-----------+-------------------------------------+----------------------------------------------+
| ``zip``   | ``zipfile`` module                  | ``zipfile`` module                           |
+-----------+-------------------------------------+----------------------------------------------+

Supported title formats
-----------------------

Other than extracting text fulltext lib is able to determine title for certain
file extensions:

+-----------+-------------------------------------+----------------------------------------------+
| Extension | Linux                               | Windows                                      |
+===========+=====================================+==============================================+
| ``doc``   | ``exiftool`` CLI tool               |                                              |
+-----------+-------------------------------------+----------------------------------------------+
| ``docx``  | ``exiftool`` CLI tool               | ``exiftool`` CLI tool                        |
+-----------+-------------------------------------+----------------------------------------------+
| ``epub``  | ``exiftool`` CLI tool               |                                              |
+-----------+-------------------------------------+----------------------------------------------+
| ``html``  | ``BeautifulSoup`` module            | ``BeautifulSoup`` module                     |
+-----------+-------------------------------------+----------------------------------------------+
| ``odt``   | ``exiftool`` CLI tool               | ``exiftool`` CLI tool                        |
+-----------+-------------------------------------+----------------------------------------------+
| ``pdf``   | ``pdfinfo`` CLI tool                |                                              |
+-----------+-------------------------------------+----------------------------------------------+
| ``pptx``  | ``pdfinfo`` CLI tool                |                                              |
+-----------+-------------------------------------+----------------------------------------------+
| ``ps``    | ``exiftool`` CLI tool               |                                              |
+-----------+-------------------------------------+----------------------------------------------+
| ``rtf``   | ``exiftool`` CLI tool               |                                              |
+-----------+-------------------------------------+----------------------------------------------+
| ``xls``   | ``exiftool`` CLI tool               | ``exiftool`` CLI tool                        |
+-----------+-------------------------------------+----------------------------------------------+
| ``xlsx``  | ``exiftool`` CLI tool               | ``exiftool`` CLI tool                        |
+-----------+-------------------------------------+----------------------------------------------+

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
    from fulltext.util import BaseBackend


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
