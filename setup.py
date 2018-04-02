# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='oasis',
    version='0.0.1',
    author="pingcap",
    author_email="yincwengo@gmail.com",

    packages=[
        "oasis",
        "oasis.datasource",
        "oasis.models",
        "oasis.libs",
    ],
    include_package_data=True,
    platforms="any",
    install_requires=[
        'scikit-learn',
        'numpy',
        'pandas',
        'requests',
        'tornado',
        'slackclient',
        "pytimeparse"
    ],
)
