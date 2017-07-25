.. figure:: https://travis-ci.org/btimby/fulltext.png
   :alt: Travis CI Status
   :target: https://travis-ci.org/btimby/fulltext

A `SmartFile`_ Open Source project. `Read more`_ about how SmartFile
uses and contributes to Open Source software.

.. figure:: http://www.smartfile.com/images/logo.jpg
   :alt: SmartFile

Introduction
------------

Fulltext is meant to be used for full-text indexing of file contents for
search applications.

Fulltext is a library that makes converting various file formats to
plain text simple. Mostly it is a wrapper around shell tools. It will
execute the shell program, scrape it's results and then post-process the
results to pack as much text into as little space as possible.

Supported formats
-----------------

* csv - ``csv``
* doc - ``/bin/antiword``
* docx - ``docx2txt``
* html - ``BeautifulSoup``, ``lxml``
* ods - stdlib, ``lxml``
* odt - stdlib, ``lxml``
* pdf - ``/bin/pdf2text``
* rtf - ``/bin/unrtf``
* text - stdlib
* xls - ``xlrd``
* xlsx - ``xlrd``
* zip - stdlib

Installing tools
----------------

Fulltext uses a number of pure Python libraries. Fulltext also uses the
command line tools: antiword, pdf2text and unrtf.

::

    $ sudo yum install antiword unrtf poppler-utils

Or for debian-based systems:

::

    $ sudo apt-get install antiword unrtf poppler-utils


Usage
-----

To use the library, simply pass a filename to the ``.get()`` module
function. A second optional argument ``default`` can provide a string to
be returned in case of error. This way, if you are not concerned with
exceptions, you can simply ignore them by providing a default. This is
like how the ``dict.get()`` method works.

::

    > import fulltext
    > fulltext.get('does-not-exist.pdf', '< no content >')
    '< no content >'
    > fulltext.get('exists.pdf', '< no content >'')
    'Lorem ipsum...'

You can pass a file-like object or a path to ``.get()`` Fulltext will try to
do the right thing, using memory buffers or temp files depending on the
backend. To write a new backend, just create a file ``be/<extension>.py`` and
define at least a ``_get_file()`` function. If you can support ``_get_path()``
more efficiently than the default implementation that uses ``_get_file()`` then
define that function as well.
