#!/usr/bin/env python
from setuptools import setup


setup(
    name="pubsubsuperfeedr",
    version="0.4.0",
    description="Library for working with Superfeedr's PubSubHubbub API",
    long_description=open('README.rst').read(),
    author="Urban Airship",
    author_email="web-team@urbanairship.com",
    url="http://github.com/urbanairship/pubsubsuperfeedr/",
    py_modules=["pubsubsuperfeedr"],
    install_requires=["feedparser", "python-dateutil", "six"],
    tests_require=["mock"],
    license="MIT License",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
)
