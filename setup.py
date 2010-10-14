#!/usr/bin/env python

from setuptools import setup


setup(name="pubsubsuperfeedr",
      version="0.3.0",
      description="Library for working with Superfeedr's PubSubHubbub API",
      author="Urban Airship",
      author_email="contact@urbanairship.com",
      url="http://github.com/urbanairship/pubsubsuperfeedr/",
      py_modules=["pubsubsuperfeedr"],
      install_requires=["feedparser", "python-dateutil"],
      license="MIT License",
)