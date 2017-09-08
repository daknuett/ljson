import ljson.slapdash.mem
import ljson.slapdash.generic

from .data import data_slapdash as data

def test_construct():
	header = ljson.slapdash.generic.SlapdashHeader({})
	table = ljson.slapdash.mem.Table(header, data)
	assert list(table) == data

	header = ljson.slapdash.generic.SlapdashHeader({})
	table = ljson.slapdash.mem.Table(header, [])
	for row in data:
		table.additem(row)

	assert list(table) == data

	table  = ljson.slapdash.mem.Table.empty()
	for row in data:
		table.additem(row)

	assert list(table) == data


def test_read():
	header = ljson.slapdash.generic.SlapdashHeader({})
	table = ljson.slapdash.mem.Table(header, data)

	assert table[{"test4": 231}].getone()["test1"] == "foo"

	assert list(table[{"test2": "bar"}]) == data[:1]

def test_edit():
	import copy
	header = ljson.slapdash.generic.SlapdashHeader({})
	table = ljson.slapdash.mem.Table(header, data)

	table[{"test1": "bar"}]["test2"] = "foolbar"

	data_ = []
	for row in data:
		row_ = copy.copy(row)
		if("test1" in row_ and row_["test1"] == "bar"):
			row_["test2"] = "foolbar"
		data_.append(row_)

	assert list(table) == data_


def test_arithmetics():
	header = ljson.slapdash.generic.SlapdashHeader({})
	table = ljson.slapdash.mem.Table(header, data)

	table.insert_stats()


	assert header.descriptor["length"] == len(data)
	assert header.descriptor["field_count"]["test1"] == 3


def test_delete():
	import copy

	header = ljson.slapdash.generic.SlapdashHeader({})
	table = ljson.slapdash.mem.Table(header, copy.copy(data))


	del(table[{"test4": 4}])

	assert not ({"test4": 4} in table)

	data_ = copy.copy(data)
	del(data_[data_.index({"test4": 4})])

	assert list(table) == data_

def test_save_open():
	header = ljson.slapdash.generic.SlapdashHeader({})
	table = ljson.slapdash.mem.Table(header, data)

	from io import StringIO

	f = StringIO()
	table.save(f)
	f.seek(0)

	table = ljson.slapdash.mem.Table.from_file(f)

	assert list(table) == data
	
