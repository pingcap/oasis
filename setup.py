#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

try:
    from setuptools import setup
except ImportError:
    print("Oasis now needs setuptools in order to build. Install it using"
          " your package manager (usually python-setuptools) or via pip (pip"
          " install setuptools).")
    sys.exit(1)


with open('requirements.txt') as requirements_file:
    install_requirements = requirements_file.read().splitlines()
    if not install_requirements:
        print("Unable to read requirements from the requirements.txt file"
              "That indicates this copy of the source code is incomplete.")
        sys.exit(2)

setup(
    name='oasis',
    version='0.0.1',
    author="PingCAP Team",
    author_email="info@pingcap.com",

    packages=[
        "oasis",
        "oasis.datasource",
        "oasis.models",
        "oasis.libs",
    ],

    include_package_data=True,

    package_data={
        '': ['oasis/models/iforest.yml',
             'oasis/models/rules.yml']
    },

    data_files=[],

    platforms="any",
    install_requires=install_requirements,

    scripts=[
        'bin/oasis-server'
    ],
)
