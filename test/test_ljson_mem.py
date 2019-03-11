import ljson.base.mem
import ljson.base.generic

from .data import data, header_descriptor, item_meg

def test_construct():
	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, data)

	assert list(table) == data

	table_postinsert = ljson.base.mem.Table(header, [])
	for row in data:
		table_postinsert.additem(row)

	assert list(table_postinsert) == data

	assert table[{"name": "peter"}].getone()["age"] == 42

	assert list(table[{"name": "peter"}]) == data[:1]


def test_write_and_read():
	from io import StringIO, BytesIO

	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, data)

	fio = StringIO()

	table.save(fio)
	fio.seek(0)

	table_in = ljson.base.mem.Table.from_file(fio)

	assert list(table_in) == data
	import pytest

	with pytest.raises(KeyError):
		assert table_in[{"foo": "bar"}]

	fio.seek(0)
	fio2 = BytesIO(fio.read().encode("utf-8"))
	table_in = ljson.base.mem.Table.from_file(fio2)

	assert list(table_in) == data

	fio3 = BytesIO()
	table_in.save(fio3)
	print(fio3.closed)
	fio3.seek(0, 0)
	fio2.seek(0, 0)
	 
	assert fio3.read() == fio2.read()

def test_edit():
	import copy
	data_ = copy.copy(data)
	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, data_)

	table[{"lname": "griffin"}]["lname"] = "Griffin"

	data_ = []

	for row in data:
		row_ = copy.copy(row)
		row_["lname"] = "Griffin"
		data_.append(row_)

	assert list(table) == data_

	table.additem(item_meg)
	assert list(table) == data_ + [item_meg]


def test_unique_check():
	import copy
	header_descriptor_ = copy.copy(header_descriptor)
	header_descriptor_["name"]["modifiers"] = ["unique"]
	header = ljson.base.generic.Header(header_descriptor_)
	table = ljson.base.mem.Table(header, data)

	table.additem(item_meg)

	import pytest

	with pytest.raises(ValueError):
		table.additem({"age": 12, "name": "chris",
				"lname": "griffin"})

def test_contains():
	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, data)


	assert {"lname": "griffin"} in table
	assert not {"lname": "griffindor"} in table


def test_delete():
	import copy
	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, copy.copy(data))

	data_ = copy.copy(data)

	del(data_[0])

	del(table[{"name": "peter"}])

	assert list(table) == data_



