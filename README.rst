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


