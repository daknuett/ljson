import ljson.base.mem
import ljson.base.generic

data = [
{
	"age": 42,
	"name": "peter",
	"lname": "griffin"
},
{
	"age": 41,
	"name": "lousie",
	"lname": "griffin"
},
{
	"age": 12,
	"name": "chris",
	"lname": "griffin"
}
]

header_descriptor = {
	"age": {"type": "int", "modifiers": []},
	"name": {"type": "str", "modifiers": []},
	"lname": {"type": "str", "modifiers": []}
}

def test_construct():
	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, data)
	
	assert list(table) == data

	table_postinsert = ljson.base.mem.Table(header, [])
	for row in data:
		table_postinsert.additem(row)

	assert list(table_postinsert) == data

	assert table[{"name": "peter"}].getone()["age"] == 42


def test_write_and_read():
	from io import StringIO

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

	table.additem({
		"age": 16,
		"name": "meg",
		"lname": "griffin"})
	assert list(table) == data_ + [{"age": 16, "name": "meg", "lname": "griffin"}]


def test_unique_check():
	import copy
	header_descriptor_ = copy.copy(header_descriptor)
	header_descriptor_["name"]["modifiers"] = ["unique"]
	header = ljson.base.generic.Header(header_descriptor_)
	table = ljson.base.mem.Table(header, data)

	table.additem({
		"age": 16,
		"name": "meg",
		"lname": "griffin"})

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



