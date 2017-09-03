import ljson.slapdash.mem
import ljson.slapdash.generic
import ljson.slapdash.disk
from io import StringIO

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
