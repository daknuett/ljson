import ljson.slapdash.mem
import ljson.slapdash.generic
import ljson.slapdash.disk
from io import StringIO

from .data import data_slapdash as data

def test_construct(tmpdir):
	import os

	header = ljson.slapdash.generic.SlapdashHeader({})
	table = ljson.slapdash.mem.Table(header, data)


	f = open(os.path.join(str(tmpdir), "file.ljson"), "w+")
	table.save(f)

	f.seek(0)
	table = ljson.slapdash.disk.Table.from_file(f)

	assert list(table) == data

	f = open(os.path.join(str(tmpdir), "file.ljson"), "w+")
	header = ljson.slapdash.generic.SlapdashHeader({})
	table = ljson.slapdash.disk.Table(header, f, reread_stats = True)

	for row in data:
		table.additem(row)

	assert list(table) == data

	f = open(os.path.join(str(tmpdir), "file.ljson"), "w+")
	table = ljson.slapdash.disk.Table.empty(f)
	for row in data:
		table.additem(row)

	assert list(table) == data



def _disk_table_from_data(tmpdir):
	import os

	header = ljson.slapdash.generic.SlapdashHeader({})
	table = ljson.slapdash.mem.Table(header, data)
	table.insert_stats()


	f = open(os.path.join(str(tmpdir), "file.ljson"), "w+")
	table.save(f)

	f.seek(0)
	table = ljson.slapdash.disk.Table.from_file(f)
	return table

def test_read(tmpdir):
	table = _disk_table_from_data(tmpdir)
	assert table[{"test4": 231}].getone()["test1"] == "foo"

	assert list(table[{"test1": "foo"}]) == [r for r  in data if "test1" in r and r["test1"] == "foo"]

	filename = table.file.name + "~"

	f = open(filename, "w")
	table.save(f)
	f.close()

	table = ljson.slapdash.disk.Table.open(filename)
	assert table[{"test4": 231}].getone()["test1"] == "foo"

	assert list(table) == data
	assert list(table[{"test1": "foo"}]) == [r for r  in data if "test1" in r and r["test1"] == "foo"]

	assert table[{"test1": "foo"}]["test1"] == [r["test1"] for r  in data if "test1" in r and r["test1"] == "foo"]

def test_edit(tmpdir):
	import copy
	table = _disk_table_from_data(tmpdir)
	table[{"test1": "bar"}]["test2"] = "foolbar"

	data_ = []
	for row in data:
		row_ = copy.copy(row)
		if("test1" in row_ and row_["test1"] == "bar"):
			row_["test2"] = "foolbar"
		data_.append(row_)

	assert list(table) == data_

	with _disk_table_from_data(tmpdir) as table:
		table[{"test1": "bar"}]["test2"] = "foolbar"

		data_ = []
		for row in data:
			row_ = copy.copy(row)
			if("test1" in row_ and row_["test1"] == "bar"):
				row_["test2"] = "foolbar"
			data_.append(row_)

		assert list(table) == data_

def test_arithmetics(tmpdir):
	table = _disk_table_from_data(tmpdir)

	table.insert_stats()


	header = table.header
	assert header.descriptor["length"] == len(data)
	assert header.descriptor["field_count"]["test1"] == 3


def test_delete(tmpdir):
	table = _disk_table_from_data(tmpdir)

	del(table[{"test4": 4}])

	assert not ({"test4": 4} in table)

	import copy

	data_ = copy.copy(data)
	del(data_[data_.index({"test4": 4})])

	assert list(table) == data_
