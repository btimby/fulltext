#!/bin/env python

import os
from setuptools import find_packages
from setuptools import setup

NAME = 'fulltext'
VERSION = '0.5'
README = os.path.join(os.path.dirname(__file__), 'README.rst')

with open(README) as f:
    DESCRIPTION = f.read()

with open('requirements.txt') as f:
    REQUIRED = f.read().splitlines()

REQUIRED = [r for r in REQUIRED if not r.startswith('git')]


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
    classifiers=(
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Text Processing :: Indexing',
    ),
)
