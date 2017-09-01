import ljson.base.mem
import ljson.base.generic
import ljson.convert.csv

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


def test_read_write():
	from io import StringIO

	header = ljson.base.generic.Header(header_descriptor)
	table = ljson.base.mem.Table(header, data)

	fio = StringIO()

	ljson.convert.csv.table2csv(table, fio)

	fio.seek(0)
	table_in = ljson.convert.csv.csv2table(fio, types = {k: v["type"] for k,v in header_descriptor.items()})

	assert list(table_in) == data

	f = StringIO()

	fio.seek(0)

	disk_table = ljson.convert.csv.csv2file(fio, f, types = {k: v["type"] for k,v in header_descriptor.items()})

	assert list(disk_table) == data
