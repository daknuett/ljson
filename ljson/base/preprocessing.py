"""

[DEVEL] make stuff ready to store them as JSON.

**Note**: This module will be used by ljson.convert.csv as well (most propably).

"""

import base64, json

TOKEN_IS_B64 = "[!!!B64ENC]"

def nothing_to_do(item):
	"""
	Some datatypes can be processed without any preprocessing,
	for instance int, bool, float, ...

	They will be just returned.
	"""
	return item

def dump_bytes(item):
	"""
	Bytes are ugly. Therefore they will be converted to a base64
	string that is UTF-8 encoded. This does increase the size of the data
	(~x3) but other tools might ot be able to process the results of
	serialized python bytes.

	**Note**: for automatic type detection (see ``guess_ljson_type_from_loaded``)
	the resulting base64 string will start with ``TOKEN_IS_B64``.

	The load_bytes will work anyways, if the token is omitted.
	"""

	decoded = base64.b64encode(item)

	return TOKEN_IS_B64 + decoded.decode("UTF-8")


def load_bytes(encoded):
	"""
	See ``dump_bytes``.
	"""

	if(encoded.startswith(TOKEN_IS_B64)):
		encoded = encoded[len(TOKEN_IS_B64):]

	encoded = encoded.encode("UTF-8")
	return base64.b64decode(encoded)

def dump_json(data):
	"""
	This function is used to dump structured data (list, dict) 
	for CSV. This is UNUSED in the usual ljson dump/load process.
	"""

	return json.dumps(data)

def load_json(data):
	"""
	See ``dump_json``.
	"""
	return json.loads(data)


dump_functions_ljson = {
	"int": nothing_to_do,
	"str": nothing_to_do,
	"float": nothing_to_do,
	"bool": nothing_to_do,
	"json": nothing_to_do,
	"bytes": dump_bytes,
}


load_functions_ljson = {
	"int": nothing_to_do,
	"str": nothing_to_do,
	"float": nothing_to_do,
	"bool": nothing_to_do,
	"json": nothing_to_do,
	"bytes": load_bytes,
}



pytype_and_ljsontype = [
	(bool, "bool"),
	(int, "int"),
	(float, "float"),
	(str, "str"),
	(bytes, "bytes"),
	(list, "json"),
	(dict, "json")
]

def guess_ljson_type_from_python(item):
	"""
	Try to guess the ljson type from the python
	datatype of the item. If the datatype is not
	supported this will raise ``ValueError``.
	"""
	for dtype, name in pytype_and_ljsontype:
		if(isinstance(item, dtype)):
			return name
	raise TypeError("unsupported datatype: {}".format(type(item)))
	

def guess_ljson_type_from_loaded(item):
	"""
	Try to guess the ljson type from the just loaded
	python object. This will check the datatype of the object.

	If the datatype is ``str`` and it starts with TOKEN_IS_B64, 
	``"bytes"`` will be returned.
	"""
	for dtype, name in pytype_and_ljsontype:
		if(isinstance(item, dtype)):
			if(dtype == str and item.startswith(TOKEN_IS_B64)):
				return "bytes"
			return name
	raise TypeError("unsupported datatype: {}".format(type(item)))



