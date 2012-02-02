#!/bin/env python

from distutils.core import setup

name = 'fulltext'
version = '0.1'
release = '1'
versrel = version + '-' + release
download_url = 'https://github.com/downloads/btimby/' + name + \
                           '/' + name + '-' + versrel + '.tar.gz'

setup(
    name = name,
    version = versrel,
    description = 'Convert files to full-text',
    long_description = 'A Python library for converting various document and media' \
                       'formats to plain text.',
    author = 'Ben Timby',
    author_email = 'btimby@gmail.com',
    maintainer = 'Ben Timby',
    maintainer_email = 'btimby@gmail.com',
    url = 'http://github.com/btimby/' + name + '/',
    download_url = download_url,
    license = 'GPLv3',
    py_modules = ["fulltext"]
)
