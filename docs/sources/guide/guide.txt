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

The table items can be accessed by using queries.
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
