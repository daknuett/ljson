"""
This module provides functions to convert ljson
tables from/to SQL tables.

**WARNING**: The SQL datatype "BINARY" and the python datatype "bytes"
might not work. 

**Note**: If one wants to use json items, these items will be stored
as "varchar" in SQL. The function table2sql_ will convert json automatically
to str, but the "sql2*" functions will not convert str to json. One can convert
the objects later.
"""

from ..base import Header, Table
from ..base.disk import Table as DiskTable

import pymysql


def _select_datatype(dtype_string):
	dtype_string = dtype_string.lower()

	dtypes_by_contains = {\
		"char": "str", 
		"text": "str", 
		"binary": "bytes", 
		"int": "int",
		"bit": "int",
		"bool": "bool",
		"dec": "float",
		"real": "float",
		"float": "float",
		"double": "float",
		"fixed": "float",
		"numeric": "float"
	}

	datatype = None
	for contains, dtype in dtypes_by_contains.items():
		if(contains in dtype_string):
			datatype = dtype
	if(datatype == None):
		raise Exception("Unable to detect ljson datatype from '{}'".format(dtype_string))
	return datatype



def sql2table(db, username, password, tablename, host = "localhost"): 
	"""
	.. _sql2table:


	Convert the SQL table to an ljson table. This function(just like sql2file_)
	**does not** parse json items automatically.

	db, username, password and host are used to log in.

	See also: sql2file_

	Returns the resulting table.
	"""
	con = pymysql.connect(db = db, user = username, password = password, host = host)

	columns = []
	dtypes_by_cols = {}
	modifiers_by_cols = {}
	with con.cursor() as cursor:
		cursor.execute("DESCRIBE {}".format(tablename))

		for colname, dtype, null, key, default, extra in cursor.fetchall():
			columns.append(colname)
			dtypes_by_cols[colname] = _select_datatype(dtype)
			mods = []
			if(not null):
				mods.append("not null")
			if(key):
				mods.append("unique")
			modifiers_by_cols[colname] = mods
	descriptor = {colname: {"type": dtypes_by_cols[colname], 
				"modifiers": modifiers_by_cols[colname]} 
		for colname in columns}
	header = Header(descriptor)
	table = Table(header, [])

	with con.cursor() as cursor:
		cursor.execute("SELECT {} FROM {}".format(",".join(columns), tablename))
		for row in cursor.fetchall():
			row = {k:v for k,v in zip(columns, row)}
			table.additem(row)
	con.close()
	return table

def sql2file(db, username, password, tablename, fout, host = "localhost"): 
	"""
	.. _sql2file:

	Convert the SQL table to an ``ljson.disk.Table``.

	This function should be used to read big tables.

	***WARNING***: ``fout`` must be opened in ``w+`` mode!

	See also: sql2table_

	Returns the resulting table.
	"""
	con = pymysql.connect(db = db, user = username, password = password, host = host)

	columns = []
	dtypes_by_cols = {}
	modifiers_by_cols = {}
	with con.cursor() as cursor:
		cursor.execute("DESCRIBE {}".format(tablename))

		for colname, dtype, null, key, default, extra in cursor.fetchall():
			columns.append(colname)
			dtypes_by_cols[colname] = _select_datatype(dtype)
			mods = []
			if(not null):
				mods.append("not null")
			if(key):
				mods.append("unique")
			modifiers_by_cols[colname] = mods
	descriptor = {colname: {"type": dtypes_by_cols[colname], 
				"modifiers": modifiers_by_cols[colname]} 
		for colname in columns}
	header = Header(descriptor)
	fout.write(header.get_header())
	fout.seek(0)

	table = DiskTable.from_file(fout)
	
	with con.cursor() as cursor:
		cursor.execute("SELECT {} FROM {}".format(",".join(columns), tablename))
		for row in cursor.fetchall():
			row = {k:v for k,v in zip(columns, row)}
			table.additem(row)
	con.close()
	return table


def table2sql(table, db, username, password, tablename, host = "localhost"):
	"""
	.. _table2sql:

	Insert the values from the given table into the 
	**already existing** SQL table.

	json items will be stored as str instances.
	"""
	
	# build the INSERT pattern:
	#
	dtypes = {k: v["type"] for k,v in table.header.descriptor.items()}
	columns = list(table.header.descriptor.keys())
	values_pattern = ",".join(["'{}'" if dtypes[colname] in ("str", "bytes", "json") else "{}" for colname in columns])
	descriptor_pattern = ",".join(columns)

	pattern = "INSERT INTO " + tablename + " (" + descriptor_pattern + ") VALUES(" + values_pattern + ")"

	con = pymysql.connect(db = db, user = username, password = password, host = host)
	with con.cursor() as cursor:
		for row in table:
			# convert json to str.
			row = {k: v if not table.header.descriptor[k]["type"] == "json" else json.dumps(v) 
				for k,v in row.items()}
			
			cursor.execute(pattern.format(*[row[colname] for colname in columns]))
	con.commit()
	con.close()

