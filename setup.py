#!/usr/bin/env python

from setuptools import setup


setup(name="pubsubsuperfeedr",
      version="0.1",
      description="Library for adding/removing feeds with Superfeedr's PubSubHubbub API",
      author="Michael Richardson",
      author_email="michael@mtrichardson.com",
      url="http://bitbucket.org/mtrichardson/pubsubsuperfeedr/",
      py_modules=["pubsubsuperfeedr"],
      install_requires=["feedparser"],
      license="MIT License",
)
