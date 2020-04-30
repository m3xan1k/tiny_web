#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

from setuptools import find_packages, setup


# Package meta-data.
NAME = 'tiny_web'
DESCRIPTION = 'WSGI-compatible framework to learn how to create tiny web applications'
URL = 'https://github.com/m3xan1k/tiny_web'
EMAIL = 'dev.serzh@gmail.com'
AUTHOR = 'Sergey Shevtsov'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.0.4'

REQUIRED = [
    'jinja2==2.11.2',
    'markupsafe==1.1.1',
    'parse==1.15.0',
    'webob==1.8.6',
    'whitenoise==5.0.1',
    'requests==2.23.0',
    'requests-wsgi-adapter==0.4.1',
]

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION

setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    packages=find_packages(exclude=["test_*"]),
    install_requires=REQUIRED,
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.6",
    ],
    setup_requires=["wheel"],
)
