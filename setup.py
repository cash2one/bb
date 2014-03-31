#!/usr/bin/env python3

if __name__ == "__main__":
    from setuptools import setup
    from distutils.core import Extension
    name = "bb"
    version = "1"
    setup(name=name, version=version, packages=[name],
          ext_modules=[Extension("bb.t", sources=["bb/test_module_t.c"])],
         )
