import ljson.base.mem
import ljson.base.disk
import ljson.base.generic
import copy, os, pytest

from .data import data, header_descriptor, item_meg

def test_read():
	from io import StringIO, BytesIO


	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, data)

	fio = StringIO()

	table.save(fio)
	fio.seek(0)

	table_in = ljson.base.disk.Table.from_file(fio)

	assert list(table_in) == data

	import pytest

	with pytest.raises(KeyError):
		assert table_in[{"foo": "bar"}]

	assert table_in[{"lname": "griffin"}]["name"] == [d["name"] for d in data]

	fio.seek(0)
	fio2 = BytesIO(fio.read().encode("utf-8"))
	table_in = ljson.base.disk.Table.from_file(fio2)

	assert list(table_in) == data


def test_edit(tmpdir):
	import copy
	data_ = copy.deepcopy(data)

	filename = os.path.join(str(tmpdir), "table.ljson")

	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, data_)

	fio = open(filename, "w+")

	table.save(fio)
	fio.seek(0)

	table = ljson.base.disk.Table.from_file(fio)
	table[{"lname": "griffin"}]["lname"] = "Griffin"
	
	data_ = []

	for row in data:
		row_ = copy.copy(row)
		row_["lname"] = "Griffin"
		data_.append(row_)

	assert list(table) == data_

	table.additem(item_meg)

	assert list(table) == data_ + [item_meg]
	
	fio = table.file

	fio.seek(0)

	table_in = ljson.base.mem.Table.from_file(fio)
	table._first_next_call = True

	assert list(table) == list(table_in)

	assert table[{"lname": "griffin"}].getone("name") == "meg"
	assert table[{"lname": "griffin"}].getone() == item_meg

	fio.seek(0)
	print(fio.readline()) # get rid of the header
	content = fio.read()
	print(content)
	fio.seek(0)
	fio.truncate(0)
	fio.write(content)
	fio.seek(0)
	table = ljson.base.disk.Table.from_file(fio)
	assert list(table) == list(table_in)

	import pytest

	with pytest.raises(RuntimeError):
		for item in table:
			table[{"name": item["name"]}]["name"] = item["name"].upper()

		for d in data_:
			d["name"] = d["name"].upper()
		assert list(table) == data_
	table.close()




def test_edit2(tmpdir):
	filename = os.path.join(str(tmpdir), "table.ljson")

	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, data)

	fio = open(filename, "w+")

	table.save(fio)
	fio.seek(0)

	table = ljson.base.disk.Table.from_file(fio)
	table[{"name": "peter"}]["name"] += "Pan"
	print(list(table))
	assert table[{"name": "peterPan"}].getone("name") == "peterPan"
		

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

def test_selection_iter(tmpdir):

	filename = os.path.join(str(tmpdir), "table.ljson")

	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, data)

	fio = open(filename, "w+")

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


def test_save(tmpdir):
	from io import StringIO
	filename = os.path.join(str(tmpdir), "table.ljson")

	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, data)

	fio = open(filename, "w+")

	table.save(fio)
	fio.seek(0)

	table_in = ljson.base.disk.Table.from_file(fio)
	assert list(table_in) == data

	f = StringIO()

	table_in.save(f)

	f.seek(0)

	table = ljson.base.disk.Table.from_file(f)

	assert list(table) == data
	
	
def test_open(tmpdir):

	filename = os.path.join(str(tmpdir), "table.ljson")

	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, data)
	

	f = open(filename, "w+")

	table.save(f)
	f.close()

	with ljson.base.mem.Table.open(filename) as table:
		assert list(table) == data
	with ljson.base.disk.Table.open(filename) as table:
		assert list(table) == data

	import pytest

	with pytest.raises(IOError):
		ljson.base.disk.Table.open(filename + "**~~")



def test_unique_check():
	import copy
	from io import StringIO
	header_descriptor_ = copy.copy(header_descriptor)
	header_descriptor_["name"]["modifiers"] = ["unique"]
	header = ljson.base.generic.Header(header_descriptor_)
	table = ljson.base.mem.Table(header, data)

	fio = StringIO()

	table.save(fio)
	fio.seek(0)

	table = ljson.base.disk.Table.from_file(fio)


	table.additem(item_meg)

	import pytest

	with pytest.raises(ValueError):
		table.additem({"age": 12, "name": "chris",
				"lname": "griffin"})

def test_contains():
	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, data)
	
	from io import StringIO
	fio = StringIO()
	table.save(fio)
	fio.seek(0)
	table = ljson.base.disk.Table.from_file(fio)

	assert {"lname": "griffin"} in table
	assert not {"lname": "griffindor"} in table

def test_delete(tmpdir):
	import copy
	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, copy.copy(data))
	import os

	filename = os.path.join(str(tmpdir), "table.ljson")

	fio = open(filename, "w+")
	table.save(fio)
	fio.seek(0)
	table = ljson.base.disk.Table.from_file(fio)

	data_ = copy.copy(data)

	del(data_[0])

	del(table[{"name": "peter"}])

	assert list(table) == data_


	table.additem(item_meg)
	del(table[{"name": "meg"}])
	assert list(table) == data_


@pytest.mark.slow
def test_speedup_delete(tmpdir, benchmark):
	benchmark(test_delete, tmpdir)
@pytest.mark.slow
def test_speedup_edit(tmpdir, benchmark):
	benchmark(test_edit, tmpdir)

@pytest.mark.slow
def test_speedup_contains(tmpdir, benchmark):
	benchmark(test_contains)
@pytest.mark.slow
def test_speedup_selection_iter(tmpdir, benchmark):
	benchmark(test_selection_iter, tmpdir)
