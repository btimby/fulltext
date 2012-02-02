#!/bin/env python

from distutils.core import setup
import radius

name = 'py-radius'
version = radius.__version__
release = '1'
versrel = version + '-' + release
download_url = 'https://github.com/downloads/btimby/' + name + \
                           '/' + name + '-' + versrel + '.tar.gz'

license = '''
Copyright (c) 1999, Stuart Bishop <zen@shangri-la.dropbear.id.au> 
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

    Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

    Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the
    distribution.

    The name of Stuart Bishop may not be used to endorse or promote 
    products derived from this software without specific prior written 
    permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

setup(
    name = name,
    version = versrel,
    description = 'RADIUS authentication module',
    long_description = 'A pure Python module that implements client side RADIUS ' \
                       'authentication, as defined by RFC2138.',
    author = 'Stuart Bishop',
    author_email = 'zen@shangri-la.dropbear.id.au',
    maintainer = 'Ben Timby',
    maintainer_email = 'btimby@gmail.com',
    url = 'http://github.com/btimby/' + name + '/',
    download_url = download_url,
    license = license,
    py_modules = ["radius"]
)

