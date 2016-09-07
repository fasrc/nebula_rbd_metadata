#!/usr/bin/env python
import os

from setuptools import setup, find_packages

VERSION = 0.1
version = os.path.join('nebula_rbd_metadata', '__init__.py')
execfile(version)

README = open('README.md').read()

setup(
    name='nebula_rbd_metadata',
    version=VERSION,
    packages=find_packages(),
    author='John Noss',
    author_email='noss@harvard.edu',
    url="https://github.com/fasrc/nebula_rbd_metadata",
    description="Sync OpenNebula template variables to RBD metadata",
    long_description=README,
    install_requires=[
        "oca>=4.10.0",
    ],
    entry_points=dict(console_scripts=['nebula_rbd_metadata = nebula_rbd_metadata.cli:main']),
    zip_safe=False
)
