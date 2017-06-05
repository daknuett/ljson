#!/usr/bin/python3

from setuptools import setup, find_packages
import sys
from os import path

if(sys.version_info.major != 3 ):
	raise SystemError("ljson requires python3")

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(
	name = "ljson",
	version = "0.1.0",
	description = "A table dataformat based on json",
	long_description = long_description,
	url = "https://github.com/daknuett/ljson",
	author = "Daniel Knüttel",
	author_email = "daknuett@gmail.com",
	license = "AGPL v3",
	classifiers = ['Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU Affero General Public License v3',
		'Programming Language :: Python :: 3'],
	keywords = "data storage table json",
	install_requires = [
#		"csv", "json" # those seem to be built-in
	],
	extras_require = {"ljson.convert.sql": "pymysql"},
	packages = find_packages()
     )


