#!/usr/bin/env python
""" cryptopy setup

    Distribution and install script for CryptoPy

    Install:
        >> python setup.py install

    Make the source distribution:
        >> python setup.py sdist --formats=gztar --force-manifest

    See http://software-carpentry.codesourcery.com/entries/build/Distutils/Distutils.html
    for more information about this file

    Copyright (c) 2002 by Paul A. Lambert
    Read LICENSE.txt for license information.
"""

from distutils.core import setup
#import sys
#assert sys.version >= '2', "Error -> Please install Python 2.0 or greater."

setup(
    # Distribution meta-data
    name         = "cryptopy",
    version      = "1.2.5",
    description  = "CryptoPy - a cryptographic framework for Python",
    author       = "Paul A. Lambert",
    author_email = "nymble@users.sourceforge.net",
    url          = "https://sourceforge.net/projects/cryptopy/",
    license      = "Released under 'artistic license', read LICENSE.txt for license information",

    # Definition of the modules and packages in the distribution
    # Note - MANIFEST.in adds additional text files
    packages     = ['',
                    'crypto',
                    'crypto.app',
                    'crypto.cipher',
                    'crypto.entropy',
                    'crypto.hash',
                    'crypto.keyedHash',
                    'crypto.passwords',
                    'fmath'],
    data_files = [ ('fmath', ['fmath/primes_1st_50k.txt']) ]    )




