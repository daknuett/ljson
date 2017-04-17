#!/usr/bin/python3

"""
Convert csv to ljson and the ohter way around.
"""

import csv, json
from ..base.generic import datatype_by_name, Header
from ..base.mem import Table
from ..base.disk import Table as DiskTable

def csv2table(fin, types = {}, modifiers = {},
		fieldnames=None, restkey=None, restval=None, dialect='excel', **fmtargs):
	"""
	.. _csv2table:

	Reads the csv table from ``fin`` and converts it to 
	a ``ljson.base.memTable``.

	The arguments fin,fieldnames,restkey,restval,dialect,fmtargs are passed to ``csv.DictReader``.

	``types`` is a dict containing the types of the columns,
	they are mapped {<columname>:<typename>}.

	``modifiers`` is a dict containing the modifiers mapped
	{<columname>:[<modifier>, <modifier>]}.

	If a column does not have an expicite type ``"str"`` is used.

	Eg:

	>>> from io import StringIO
	>>> fin = StringIO("id,name\\n1,foo\\n2,bar\\n3,baz")
	>>> table = csv2table(fin, types = {"id": "int", "name":"str"}, modifiers = {"id": ["unique"]})
	>>> list(table)
	[{'name': 'foo', 'id': 1}, {'name': 'bar', 'id': 2}, {'name': 'baz', 'id': 3}]


	**Note**: to convert files csv2file_ should be used.

	Returns: the table
	"""

	reader = csv.DictReader(fin, 
			fieldnames = fieldnames, 
			restkey = restkey, 
			restval = restval,
			dialect = dialect,
			**fmtargs)

	descriptor = {}
	converters = {}
	for fieldname in reader.fieldnames:
		descriptor[fieldname] = {"modifiers": []}
		if(fieldname in types):
			descriptor[fieldname]["type"] = types[fieldname]
			converters[fieldname] = datatype_by_name[types[fieldname]]
		else:
			descriptor[fieldname]["type"] = "str"
		if(fieldname in modifiers):
			descriptor[fieldname]["modifiers"] = modifiers[fieldname]

	header = Header(descriptor)
	table = Table(header, [])

	for row in reader:
		# This converts all non-str elements.
		# it is kind of hard to read.
		# This equals
		#
		#	 for k,v in row.items():
		#		if(k in converters):
		#			row[k] = converters[k](v)
		#
		row = {k: converters[k](v) if k in converters else v for k,v in row.items()}
		table.additem(row)
	return table
		
	
			
	
def csv2file(fin, fout, types = {}, modifiers = {},
		fieldnames=None, restkey=None, restval=None, dialect='excel', **fmtargs):
	"""
	.. _csv2file:

	Converts the csv file to a ljson file. Reads csv from ``fin`` and writes to ``fout``.

	The main difference to csv2table_ is that csv2file uses the on-disk implementation.
	
	This function should be used if one wants to convert just the files without using the data.

	**See also**: csv2table_

	Returns: the table
	"""
	
	reader = csv.DictReader(fin, 
			fieldnames = fieldnames, 
			restkey = restkey, 
			restval = restval,
			dialect = dialect,
			**fmtargs)

	descriptor = {}
	converters = {}
	for fieldname in reader.fieldnames:
		descriptor[fieldname] = {"modifiers": []}
		if(fieldname in types):
			descriptor[fieldname]["type"] = types[fieldname]
			converters[fieldname] = datatype_by_name[types[fieldname]]
		else:
			descriptor[fieldname]["type"] = "str"
		if(fieldname in modifiers):
			descriptor[fieldname]["modifiers"] = modifiers[fieldname]

	header = Header(descriptor)

	fout.write(header.get_header())
	fout.seek(0)

	table = DiskTable(header, fout)

	for row in reader:
		# This converts all non-str elements.
		# it is kind of hard to read.
		# This equals
		#
		#	 for k,v in row.items():
		#		if(k in converters):
		#			row[k] = converters[k](v)
		#
		row = {k: converters[k](v) if k in converters else v for k,v in row.items()}
		table.additem(row)
	return table

def table2csv(table, fout, restval='', extrasaction='raise', dialect='excel', *args, **kwds):
	"""
	Convert the given ljson table to csv.

	The arguments ``restval='', extrasaction='raise', dialect='excel', *args, **kwds`` are
	passed to ``csv.DictWriter``.

	**Hint**: Converting files can be done by using the on-disk implementation:

	>>> from ljson.base.disk import Table
	>>> from ljson.convert.csv import table2csv
	>>> fin = open("test.lson", "r+")
	>>> table = Table.from_file(fin)
	>>> fout = open("test.csv", "w")
	>>> table2csv(table, fout)

	Returns: None
	"""
	fieldnames = list(table.header.descriptor.keys())
	# XXX I do not know why but ONLY in doctest
	# this gets messed up. The field "__type__"
	# should get deleted in Header.__init__.
	# FIXME explan this.
	if("__type__" in fieldnames):
		del(fieldnames[fieldnames.index("__type__")])
	writer = csv.DictWriter(fout, fieldnames, 
			restval = restval,
			extrasaction = extrasaction,
			dialect = dialect,
			*args,
			**kwds)
	writer.writeheader()
	for row in table:
		row = {k: v if not table.header.descriptor[k]["type"] == "json" else json.dumps(v) 
			for k,v in row.items()}
		writer.writerow(row)

