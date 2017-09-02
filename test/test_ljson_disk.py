import ljson.base.mem
import ljson.base.disk
import ljson.base.generic
import copy

data = [
{
	"age": 42,
	"name": "peter",
	"lname": "griffin"
},
{
	"age": 41,
	"name": "louise",
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

def test_read():
	from io import StringIO


	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, data)

	fio = StringIO()

	table.save(fio)
	fio.seek(0)

	table_in = ljson.base.disk.Table.from_file(fio)

	assert list(table_in) == data

def test_edit():
	from io import StringIO

	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, data)

	fio = StringIO()

	table.save(fio)
	fio.seek(0)

	table = ljson.base.disk.Table.from_file(fio)
	table[{"lname": "griffin"}]["lname"] = "Griffin"
	
	data_ = []

	for row in data:
		row_ = row
		row_["lname"] = "Griffin"
		data_.append(row_)

	assert list(table) == data_

	table.additem({
		"age": 16,
		"name": "meg",
		"lname": "griffin"})
	fio.seek(0)
	print(fio.read())
	fio.seek(0)

	assert list(table) == data + [{"age": 16, "name": "meg", "lname": "griffin"}]
	
	fio.seek(0)

	table_in = ljson.base.mem.Table.from_file(fio)
	table._first_next_call = True

	assert list(table) == list(table_in)


def test_contexts():
	from io import StringIO

	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, data)

	fio = StringIO()

	table.save(fio)
	fio.seek(0)

	with ljson.base.disk.Table.from_file(fio) as table:
		assert list(table) == data

def test_zipping():
	from io import StringIO

	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, data)

	fio = StringIO()

	table.save(fio)
	fio.seek(0)

	table_in = ljson.base.disk.Table.from_file(fio)

	for row_data, row_mem, row_disk in zip(data, table, table_in):
		assert row_data == row_mem
		assert row_data == row_disk

def test_selection_iter():
	from io import StringIO

	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, data)

	fio = StringIO()

	table.save(fio)
	fio.seek(0)

	table_in = ljson.base.disk.Table.from_file(fio)

	for row in table_in[{"lname": "griffin"}]:
		assert row["lname"] == "griffin"


	table_in[{"name": "chris"}]["lname"] = "peters"

	for row in table_in[{"lname": "griffin"}]:
		assert row["lname"] == "griffin"
	for row in table_in[{"lname": "peters"}]:
		assert row["name"] == "chris"

	

