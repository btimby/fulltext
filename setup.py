#!/bin/env python

import os
from setuptools import find_packages
from setuptools import setup

name = 'fulltext'
version = '0.4'
release = '1'
readme = os.path.join(os.path.dirname(__file__), 'README.rst')
versrel = version + '-' + release
long_description = file(readme).read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

required = [r for r in required if not r.startswith('git')]


setup(
    name=name,
    version=versrel,
    description='Convert binary files to plain text for indexing.',
    long_description=long_description,
    author='Ben Timby',
    author_email='btimby@gmail.com',
    maintainer='Ben Timby',
    maintainer_email='btimby@gmail.com',
    url='http://github.com/btimby/' + name + '/',
    license='GPLv3',
    packages=find_packages(),
    install_requires=required,
    classifiers=(
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Text Processing :: Indexing',
    ),
)
