Quickstart
**********

Creating New Tables
===================

To create a new table one has to use the memory
implementation. This is quite simple::

	from ljson import Table, Header

	# create the header
	header = Header({"id": {"type": "int", "modifiers":["unique"]},
			"name": {"type": "str", "modifiers": []},
			"age": {"type": "int", "modifiers":[]}
			})
	table = Table(header, [])


If one wants to use the on disk implementation the table has
to be saved::

	from ljson.disk import Table as DiskTable

	# save the table on the disk
	fio = open("test.ljson", "w+")
	table.save(fio)

	# use the on-disk implementation
	table = DiskTable.from_file(fio)

Inserting Data	
===============

Inserting data into a table is done by using the method
``additem`` that takes a ``dict`` containing the data::

	table.additem({"id": 0, "name": "Peter", "age": 20})
	table.additem({"id": 1, "name": "Gustav", "age": 17})
	table.additem({"id": 2, "name": "Peter", "age": 21})
	table.additem({"id": 3, "name": "Sally", "age": 17})


Using Tables
============

ljson tables are using a quite pythonic interface.
Accessing elements is done by either iterating::

	for row in table:
		# do something with row
		# row is a dict containing the data
		print(row)

**Note**: You cannot set data using this method.

Or by using queries.
A query is basically indexing the table with a dict.
This returns a Selector object. A selector is iterable
and single elements can be accessed by the method
``getone``::

	for row in table[{"name": "Peter"}]:
		print(row)

	table[{"age": 17}]["age"] = 18

	peter_1_age = table[{"id":0}].getone("age")


If the dict contains more than one key value pair
all conditions will be joined by logical ``and``.

Cookbook
********

This chapter contains some recipes for ljson.

Simple Min and Max
==================

As ljson tables are iterable, the default min and max
functions will work::

	youngest = min(table, key = lambda row: row["age"])

As suggested in "Data Science from Scratch" by Joel Grus one
can write a simple function for that::

	def picker(keyname):
		return lambda row: row[keyname]

	oldest = max(table, key = picker("age"))

Min and Max and Queries
=======================

Selectors are iterable too, so... guess what::

	oldest_peter = max(table[{"name":"peter"}], key = picker("age"))

Converting CSV to LJSON
=======================

Assuming you have a file called ``input.csv`` and you want
to convert it to a file ``output.ljson``, you can use the
function ``ljson.convert.csv.csv2file``. At first take
a look at your file::

	id,age,name
	0,20,Peter
	1,17,Gustav
	2,21,Peter
	3,17,Sally

Now open the files and convert them::

	from ljson.convert.csv import *

	fio = open("input.csv", "r")
	fout = open("output.ljson", "w")
	disk_table = csv2file(fio, fout, types = {"name": "str", "id": "int", "age": "int"})
	fio.close()
	fout.close()

This is the content of output.ljson::

	{"__type__": "header", "id": {"type": "int", "modifiers": []}, "age": {"type": "int", "modifiers": []}, "name": {"type": "str", "modifiers": []}}
	{"id": 0, "age": 20, "name": "Peter"}
	{"id": 1, "age": 17, "name": "Gustav"}
	{"id": 2, "age": 21, "name": "Peter"}
	{"id": 3, "age": 17, "name": "Sally"}

Converting LJSON to CSV
=======================

This is pretty simple as well. It is recommended to use the
on disk implementation for those conversions, as they avoid
loading tons of data into your ram.

::

	fout = open("output.csv", "w")
	table2csv(disk_table, fout)
	fout.close()

Using Context Managers
======================

Since version 0.1.0 ljson tables are context managers. This
makes it easy to manage disk tables::

	with DiskTable.open("output.json") as table:
		with open("output.csv", "w") as fout:
			table2csv(table, fout)

	# now both fout and table are closed properly.


Deleting Items
==============

Deleting rows is supported since 0.1.1::

	with DiskTable.open("output.json") as table:
		del(table[{"id": 0}])

Gotchas
*******

In *v0.3.0* a new feature has been added:
``LjsonQueryResult`` s. Those objects are returned by
``LjsonSelector.__getitem__`` and should fulfill two
purposes:

- Behave like a list for nearly everything
- Make it possible to edit tables in a pythonic way.

Therefore something like this is possible::

	with DiskTable.open("data.json") as table:
		table[{"id": 0}]["age"] += 1

Which is pretty nice. But it also should work like a list,
so::

	with DiskTable.open("data.json") as table:
		result = table[{"id": 0}]["age"] + [1]

Will produce ``[21, 1]``.

So unluckily::

	with DiskTable.open("data.json") as table:
		table[{"id": 0}]["age"] = table[{"id": 0}]["age"] + 1

Will fail (and in general this leads to undefined
behaviour).

The ``LjsonQueryResult`` class overrides all ``__i*__``
methods, while all other methods are passed to the
underlaying ``list``.
