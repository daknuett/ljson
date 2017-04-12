ljson -- Line JSON
******************

What is ljson?
==============

ljson is an attempt to create a database model suiting the
needs of modern data procession. It is designed to work
faster than usual json, but to keep the simple but yet
elegant object representation.

ljson can be used instead of pure json to increase the
performance when accessing a large set of data.

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

Usage
=====

Without a Python Module
-----------------------

ljson is designed to work without any third party python
modules. One can read ljson data with the python built-in
json module::

	import json
	ljson = '''\
	{"id": 1, "name": "foo"}
	{"id": 2, "name": "bar"}'''

	for line in ljson.split("\n"):
		print(json.loads(line))

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
tables)::

	import ljson
	header = ljson.Header({"id": {"type": "int",
	"modifiers":["unique"]}, "name": {"type": "str",
	"modifiers": []}})

	table = ljson.Table(header, 
	[{"id": 1, "name": "foo"}, 
	{"id": 2, "name": "bar"}, {"id": 3, "name": "bar"}])


