#!/usr/bin/env python

from distutils.core import setup
import korbit


def readme():
    try:
        with open('README.rst') as f:
            return f.read()
    except:
        return '(Could not read from README.rst)'


setup(name='korbit',
      py_modules=['korbit.api', 'korbit.models'],
      version=korbit.__version__,
      description='A Python wrapper for Korbit API',
      long_description=readme(),
      author=korbit.__author__,
      author_email=korbit.__email__,
      url='http://github.com/suminb/korbit',
      packages=[])
