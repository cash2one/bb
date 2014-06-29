#!/usr/bin/env python3

from distutils.core import setup, Extension
name = "bb"
version = "1"
setup(
    name=name,
    version=version,
    packages=[name],
    scripts=[name[0]],
    )
