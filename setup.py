#!/bin/env python

import os
import sys
from os.path import dirname
from os.path import join as pathjoin
from setuptools import find_packages
from setuptools import setup


NAME = 'fulltext'
VERSION = '0.7'
if os.name == 'nt' and not sys.maxsize > 2 ** 32:
    # https://github.com/btimby/fulltext/issues/79
    raise RuntimeError("Python 32 bit is not supported")


with open(pathjoin(dirname(__file__), 'README.rst')) as f:
    DESCRIPTION = f.read()

REQUIRED, REQUIRED_URL = [], []

with open('requirements.txt') as f:
    for line in f.readlines():
        if 'http://' in line or 'https://' in line:
            REQUIRED_URL.append(line)

        else:
            REQUIRED.append(line)


setup(
    name=NAME,
    version=VERSION,
    description='Convert binary files to plain text for indexing.',
    long_description=DESCRIPTION,
    author='Ben Timby',
    author_email='btimby@gmail.com',
    maintainer='Ben Timby',
    maintainer_email='btimby@gmail.com',
    url='http://github.com/btimby/' + NAME + '/',
    license='GPLv3',
    packages=find_packages(),
    install_requires=REQUIRED,
    dependency_links=REQUIRED_URL,
    include_package_data=True,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Indexing',
    ),
)
