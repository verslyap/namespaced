#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages
from Cython.Build import cythonize

setup(name='namespaced',
      version='0.1',
      description='Linux kernel namespace tool',
      author='Adam Verslype',
      author_email='verslyap@gmail.com',
      setup_requires=["cython"],
      scripts=['namespaced.py'],
      #packages=find_packages(where="./src"),
      install_requires=['argparse','dbus','enum','logging','yaml','importlib-metadata; python_version >= "3.10"'],
      py_modules=['Namespace','Namespaced','NSManager'],
      ext_modules = cythonize(["/root/namespaced/src/cNSWorker.pyx"])
     )