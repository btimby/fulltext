.. figure:: https://travis-ci.org/btimby/fulltext.png
   :alt: Travis CI Status
   :target: https://travis-ci.org/btimby/fulltext

.. figure:: https://www.smartfile.com/assets/img/smartfile-logo-new.png
   :alt: SmartFile

A `SmartFile`_ Open Source project.

Introduction
------------

Fulltext extracts texts from various document formats. It can be used as the
first part of search indexing, document analysis etc.

Fulltext differs from other libraries in that it tries to use file data in the
form it is given. For most backends, a file-like object or path can be handled
directly, removing the need to write temporary files.

Fulltext uses native python libraries when possible and utilizes CLI tools
when necessary, for example, the following CLI tools are required.

 * antiword - Legacy .doc (Word) format.
 * unrtf - .rtf format.
 * pdf2text (poppler-utils) - .pdf format.

Supported formats
-----------------

* csv - Uses Python ``csv`` module.
* doc - Uses ``/bin/antiword`` CLI tool.
* docx - Uses Python ``docx2txt`` module.
* html - Uses Python ``BeautifulSoup`` module.
* ods - Uses Python ``lxml``, ``zipfile`` modules.
* odt - Uses Python ``lxml``, ``zipfile`` modules.
* pdf - Uses ``/bin/pdf2text`` CLI tool.
* rtf - Uses ``/bin/unrtf`` CLI tool.
* text - Default backend that uses various Python stdlib modules to extract
         strings from arbitrary (possibly) binary files.
* xls - Uses Python ``xlrd`` module.
* xlsx - Uses Python ``xlrd`` module.
* zip - Uses Python ``zipfile`` module.

Installing tools
----------------

Fulltext uses a number of pure Python libraries. Fulltext also uses the
command line tools: antiword, pdf2text and unrtf. To install the required
libraries and CLI tools, you can use your package manager.

.. code:: bash

    $ sudo yum install antiword unrtf poppler-utils libjpeg-dev

Or for debian-based systems:

.. code:: bash

    $ sudo apt-get install antiword unrtf poppler-utils libjpeg-dev


Usage
-----

Fulltext uses a simple dictionary-style interface. A single public function
``fulltext.get()`` is provided. This function takes an optional default
parameter which when supplied will supress errors and return that default if
text could not be extracted.

.. code:: python

    > import fulltext
    > fulltext.get('does-not-exist.pdf', '< no content >')
    '< no content >'
    > fulltext.get('exists.pdf', '< no content >'')
    'Lorem ipsum...'

You can pass a file-like object or a path to ``.get()`` Fulltext will try to
do the right thing, using memory buffers or temp files depending on the
backend.


Custom backends
---------------

To write a new backend, you need to do two things. First, create a python
module that implements the interface that Fulltext expects. Second, define an
environment variable that informs Fulltext where to find your module.

.. code:: python

    # Tell Fulltext what file extensions your backend supports.
    EXTENSIONS = ('foo', 'bar')


    def _get_file(f, **kwargs):
        # Extract text from a file-like object. This should be defined when
        # possible.
        pass


    def _get_path(path, **kwargs):
        # Extract text from a path. This should only be defined if it can be
        # done more efficiently than having Python open() and read() the file,
        # passing it to _get_file().
        pass

If you only implement ``_get_file`` Fulltext will open any paths and pass them
to that function. Therefore if possible, define at least this function. If
working with file-like objects is not possible and you only define
``_get_path`` then Fulltext will save any file-like objects to a temporary
file and use that function. Sometimes it is advantageous to define both
functions in cases when you can do each efficiently.

If you have questions about writing a backend, see the `backends/`_ directory
for some examples.

.. _backends/: fulltext/backends/

Once written, simply define an environment variable ``FULLTEXT_PATH`` to
contain paths to your backend modules.

.. code:: bash

    FULLTEXT_PATH=/path/to/my/module;/path/to/other/module python myprogram.py
