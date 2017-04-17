ljson -- Line JSON
******************

.. contents::


Quicklinks
==========

- `The Documentation <https://daknuett.github.io/ljson>`_
- `The github.com repo <https://github.com/daknuett/ljson>`_
- `The PyPi repo <https://pypi.python.org/pypi/ljson/>`_

What is ljson?
==============

ljson is an attempt to create a database model suiting the
needs of modern data procession. It is designed to work
faster than usual json, but to keep the simple but yet
elegant object representation.

ljson can be used instead of pure json to increase the
performance when accessing a large set of data.


Why ljson?
==========

There are a **lot** data storage formats out there: XML,
JSON, CSV, SQL, NOSQL, binary packed, GNU-DB,...

Some of them are designed to store complete databases (SQL,
NOSQL, ...) and some are designed to store tables. And of
course there are JSON and XML. They can be used to store
more complex objects, are human-readable and data is stored
in just one file.

But they suffer from one problem: If one wants to alter the
data in the file he has to read the complete file and store
all the data in his RAM. This is slow, maybe impossible
(*Big Data*) and insecure. If the process cannot complete
the operation properly this might corrupt all data.

ljson tries to bypass this by using a mixture of CSV (line
based) and JSON (object based): 

Every line is one object. If one wants to add another object
he just opens the file in append mode and adds one line. If
one line is corrupted the rest of the file is still valid.

Operating on large sets of objects is also possible by
reading the file line by line.

Especially asynchronous operations can be performed easily,
as the main part of the file stays untouched (unless you
alter objects. Then the file has to be re-written).

Design
======

ljson is designed to be stored in files, the definition
of a ljson file is::

	<ljson_file> = [<header>\n]<ljson_content>
	<ljson_content> = <json_object>{\n<json_object>}

``<json_object>`` can be any json object, as described on
`json.org <http://json.org/>`_.

Header
------

The header is a special json object that describes the data
in the file. A header must be in the following format::

	<header> = "{ \"__type__\": \"header\"," <fieldname>": {" "\"type\":" <type>", \"modifiers\":" <modifiers> "}"
	<type> = "\"int\"" | "\"str\"" | "\"bool\"" | "\"float\"" | "\"null\"" | "\"bytes\""
	<modifiers> = "[" [<modifier> {","<modifier>}] "]"
	<modifier> = "\"unique\"" | "\"not null\"" 

The header is required by the on-disk implementation.

Datatypes
---------

If you use ljson you are restricted to the following python
data types (and their ljson types):

- ``int``: ``"int"``
- ``str``: ``"str"``
- ``bool``: ``"bool"``
- ``float``: ``"float"``
- ``bytes``: ``"bytes"``
- ``dict``: ``"json"``
- ``list``: ``"json"``

Because it is possible to convert all data types to one of
these it is possible to store any kind of data.

Usage
=====

Without a Python Module
-----------------------

ljson is designed to work without any third party python
modules. One can read ljson data with the python built-in
json module:

>>> import json
>>> ljson = '{"id": 1, "name": "foo"}\n{"id": 2, "name": "bar"}'
>>> for line in ljson.split("\n"):
... 	print(json.loads(line))
...
{'name': 'foo', 'id': 1}
{'name': 'bar', 'id': 2}

And this should always be the preferred way to access ljson
data, if all data is required. 

If one wants to access specific fields it is better to use
the ljson python module:

With the ljson Module
---------------------

Using the ljson Module is simple and efficient if one wants
to access just some fields, not the complete file.

There are two base implementations: ``ljson.base.mem`` that
loads the file content into the RAM. This is way faster and
supports files without a header and one is able to construct
the Table without a file.

The second implementation is ``ljson.base.disk``. This
implementation does not load any data into RAM. If you are
accessing huge sets you should use this implementation.

Creating a table is simple (at least for the memory
tables):

>>> import ljson
>>> header = ljson.Header({"id": {"type": "int", "modifiers":["unique"]}, "name": {"type": "str", "modifiers": []}})
>>> table = ljson.Table(header, [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}, {"id": 3, "name": "bar"}])


One can access items using python's built-in ``__getitem__``
and ``__setitem__``:

>>> table[{"id": 1}]["name"]
['foo']
>>> list(table[{"id": 1}]) 
[{'name': 'foo', 'id': 1}]

The table "index" must be a dict. This allows to access
non-unique rows, like this:

>>> list(table[{"name":"bar"}])
[{'id': 2, 'name': 'bar'}, {'id': 3, 'name': 'bar'}]


Using ljson to store data
-------------------------

Using ljson to store data is pretty simple:

>>> from io import StringIO
>>> fout = StringIO()
>>> table.save(fout)
>>> fout.seek(0)
0
>>> fout.read()
'{"name": {"type": "str", "modifiers": []}, "__type__": "header", "id": {"type": "int", "modifiers": ["unique"]}}\n{"name": "foo", "id": 1}\n{"name": "bar", "id": 2}\n{"name": "bar", "id": 3}'
>>> fout.seek(0)
0
>>> table2 = ljson.Table.from_file(fout)
>>> list(table2)
[{'id': 1, 'name': 'foo'}, {'id': 2, 'name': 'bar'}, {'id': 3, 'name': 'bar'}]


Reading and writing csv files is pretty simple, too:

>>> from ljson.convert.csv import table2csv, csv2table
>>> fout = StringIO()
>>> table2csv(table, fout)
>>> fout.seek(0)
0
>>> fout.read()
'id,name\r\n1,foo\r\n2,bar\r\n3,bar\r\n'
>>> fout.seek(0)
0
>>> table2 = csv2table(fout, types = {"id": "int", "name":"str"})
>>> list(table2)
[{'id': 1, 'name': 'foo'}, {'id': 2, 'name': 'bar'}, {'id': 3, 'name': 'bar'}]


Todos
=====

- store bytes as b64
- fix the sql bytes representation
