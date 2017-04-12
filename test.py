# coding: utf-8

from ljson.base.generic import Header
from ljson.base.mem import Table

from ljson.base import disk

header = Header({"id": {"type": "int", "modifiers":["unique"]}, "name": {"type": "str", "modifiers": []}})
table = Table(header, [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}, {"id": 3, "name": "bar"}])

print(table[{"id": 1}]["name"])
print({"id": 1} in table)

print(table[{"id": 3}]["name"])
table[{"id": 3}]["name"] = "baz"
print(table[{"id": 3}]["name"])

print(max(table, key = lambda r: r["id"]))

table[{"id": 3}]["name"] = "bar"
print(table[{"name": "bar"}]["id"])

fout = open("test.ljson", "w")
table.save(fout)
fout.close()
#
#print()
#
f = open("test.ljson", "r+")
#
disktable = disk.Table.from_file(f)
#
disktable[{"id": 3}]["name"] = "bongo"
#
for row in disktable:
	print(row)
