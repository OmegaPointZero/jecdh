# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

try:
    long_description = open("README.md").read()
except IOError:
    long_description = ""

setup(
    name="jecdh",
    version="0.0.1",
    description="A small ECDH module, with a Py4J backend.",
    license="MIT",
    author="OmegaPointZero",
    packages=find_packages(),
    install_requires=open("requirements.txt").readlines(),
    long_description=long_description,
    test_suite="tests",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
    ]
)
