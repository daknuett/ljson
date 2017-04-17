# coding: utf-8

from ljson.base.generic import Header
from ljson.base.mem import Table
from ljson.base import disk
from ljson.convert.csv import table2csv, csv2table
from io import StringIO
import json

header = Header({"id": {"type": "int", "modifiers":["unique"]}, 
		"name": {"type": "str", "modifiers": []}, 
		"object":{"type": "json", "modifiers": []}})
table = Table(header, [{"id": 1, "name": "foo", "object": {"next": 2}}, 
			{"id": 2, "name": "bar", "object": {"next": 3}}, 
			{"id": 3, "name": "bar", "object": {"next": 1}}])


print("TESTING QUERIES")
print(table[{"id": 1}]["name"])
print({"id": 1} in table)

print(table[{"id": 3}]["name"])
table[{"id": 3}]["name"] = "baz"
print(list(table[{"id": 3}]))

print("TESTING built-in functions")
print(max(table, key = lambda r: r["id"]))

print("TESTING setter")
table[{"id": 3}]["name"] = "bar"
print(table[{"name": "bar"}]["id"])

print("TESTING READ/WRITE")
fout = open("test.ljson", "w")
table.save(fout)
fout.close()
#
print()
#
f = open("test.ljson", "r+")
#
disktable = disk.Table.from_file(f)
#
disktable[{"id": 3}]["name"] = "bongo"
#
for row in disktable:
	print(row)

print("TESTING CONVERSION")
fout = StringIO()

table2csv(table, fout)
fout.seek(0)
print(fout.read())
fout.seek(0)
print(list(csv2table(fout, types = {"id": "int", "name": "str", "object": "json"})))

print("DONE")
