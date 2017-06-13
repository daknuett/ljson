# coding: utf-8
from ljson.slapdash.mem import *
table = Table(SlapdashHeader({}), [])
table.additem({"foo": "bar", "cnt": 12, "store": True})
table.additem({"foo": ["bar"], "cnt": 12, "store": True})
table.additem({"foo": 23, "cnt": 12, "store": True})
get_ipython().magic('save test.py 1-6')
table.header.descriptor["field_count"]["foo"] / table.header.descriptor["length"]
table.additem({"bar": "foo", "cnt": 12, "store": True})
table.header.descriptor["field_count"]["foo"] / table.header.descriptor["length"]
