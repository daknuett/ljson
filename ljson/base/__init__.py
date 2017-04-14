#!/usr/bin/python3

"""
The base ljson implementation.

This package provides base functionality, 
like getter and setter interface.

Creating a ljson table is pretty easy.

>>> from ljson import base 
>>> header = base.Header({"id": {"type": "int", "modifiers":["unique"]}, "name": {"type": "str", "modifiers": []}})
>>> table = base.Table(header, [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}, {"id": 3, "name": "bar"}])

	***NOTE***: The default implementation is the in-memory implementation.
	If one wants to use the on-disk implementation he has to use
	``ljson.base.disk`` instead. The on disk implementation does not
	support instantiation with data, you have to use a file containing
	at least a header instead.

Accessing Fields form the ljson table is pretty easy, too:

>>> table[{"id": 1}]["name"]
['foo']
>>> table[{"id": 3}]["name"] = "baz"
>>> table[{"id": 3}]["name"]
['baz']

Now you might have recognized that the first "index" is a dict and the
result is a list. This is because the rows might be not unique:

>>> table[{"id": 3}]["name"] = "bar"
>>> table[{"name": "bar"}]["id"]
[2, 3]

"""

__all__ = ['mem', 'disk']
__author__ = "Daniel Knüttel"

from .mem import Table
from .generic import Header
