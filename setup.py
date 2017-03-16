# coding: utf-8
import os
from setuptools import setup


def read_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

VERSION = (0, 1, 0)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))


setup(
    name="sigepy",
    version=__versionstr__,
    author=u"Stored e-Commerce",
    author_email="contato@stored.com.br",
    description=("Wrapper SIGEP Correios"),
    license="BSD",
    keywords="correios sigep",
    url="https://github.com/stored/sigepy",
    packages=['sigep', ],
    long_description=read_file('README.md'),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    install_requires=[
        r for r in read_file('requirements.txt').split('\n') if r],
)