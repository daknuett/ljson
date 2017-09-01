import ljson.slapdash.mem
import ljson.slapdash.generic

data = [
{
	"test1": "foo",
	"test2": "bar",
	"test3": "baz"
},
{
	"test4": 4
},
{
	"test1": "foo",
	"test2": "fool",
	"test4": 231
},
{
	"test1": True,
	"test2": "baz"
}
]

def test_construct():
	header = ljson.slapdash.generic.SlapdashHeader({})
	table = ljson.slapdash.mem.Table(header, data)
	assert list(table) == data

	header = ljson.slapdash.generic.SlapdashHeader({})
	table = ljson.slapdash.mem.Table(header, [])

	for row in data:
		table.additem(row)

	assert list(table) == data


def test_read():
	header = ljson.slapdash.generic.SlapdashHeader({})
	table = ljson.slapdash.mem.Table(header, data)
	
	assert table[{"test4": 231}].getone()["test1"] == "foo"

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
	import pytest
	header = ljson.slapdash.generic.SlapdashHeader({})
	table = ljson.slapdash.mem.Table(header, data)
	
	table.insert_stats()


	assert header.descriptor["length"] == len(data)
	assert header.descriptor["field_count"]["test1"] == 3
