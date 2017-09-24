"""
Some generic functions and classes for ljson.

They are used by the memory and the disk implementation.
"""
import json

datatypes = (int, str, float, bool, bytes, dict, list)

datatype_by_name = {"int": int, "str": str, "float": float, "bytes": bytes, "bool": bool, "json": json.loads}
python_datatype_by_name = {"int": int, "str": str, "float": float, "bytes": bytes, "bool": bool, "json": (list, dict)}
inversed_datatypes = {}
for k, v in python_datatype_by_name.items():
	if(not isinstance(v, tuple)):
		inversed_datatypes[v] = k
	else:
		for pytype in v:
			inversed_datatypes[pytype] = k

class Header(object):
	def __init__(self, descriptor):
		self.descriptor = descriptor
		if("__type__" in self.descriptor):
			del(self.descriptor["__type__"])


	def __repr__(self):
		return "{mymod}.{myname}({descriptor})".format(mymod = type(self).__module__,
				myname = type(self).__name__,
				descriptor = self.descriptor)

	@staticmethod
	def from_file(fin):
		"""
		Construct the header from the file.
		"""

		line = fin.readline()
		while(line.isspace()):
			line = fin.readline()
		data = json.loads(line)
		if(not "__type__" in data or data["__type__"] != "header"):
			fin.seek(0)
			descriptor = {}
			for k in data.keys():
				descriptor[k] = {"type": None, "modifiers": []}
			return Header(descriptor), True
		del(data["__type__"])
		return Header(data), False

	def check_data(self, key, value):
		"""
		Typecheck the given key value pair
		"""
		if(not key in self.descriptor):
			raise KeyError("Unknown key: {}".format(repr(key)))

		if(not isinstance(value, datatypes)):
			return False

		if(self.descriptor[key]["type"] == None):
			return True

		if(isinstance(value, python_datatype_by_name[self.descriptor[key]["type"]])):
			return True
		return False

	def get_header(self):
		"""
		Return a JSON header.
		"""
		header = self.descriptor
		header["__type__"] = "header"

		return json.dumps(header)


class LjsonTable(object):
	def __init__(self):
		self.header = None
	def save(self, fout):
		"""
		Save the table to the given file.
		"""
	def __getitem__(self, dct):
		"""
		Select rows by the dict dct.
		Returns a LjsonSelector object.

		Using dict as index is required to provide
		"search functionality".

		See also the ljson.base documentation.
		"""
		pass
	def __next__(self):
		"""
		Returns: the next row of the table
		"""
		pass
	@staticmethod
	def from_file(fin):
		"""
		Construct the table from the given file.
		"""
		pass
	@staticmethod
	def open(filename):
		"""
		Equivalent to ``Table.from_file(open(filename, "r+"))``
		"""
		pass
	def additem(self, row):
		"""
		Add the row to the table.
		"""
	def __contains__(self, dct):
		"""
		Check if there is at least one row matching the selector ``dct``

		Example::

			{"id": 4} in table
		"""
		pass
	def __delitem__(self, dct):
		"""
		Delete all matching items.
		"""
		pass


class LjsonSelector(object):
	def __init__(self):
		pass
	def __getitem__(self, column):
		"""
		Return the column values as a list
		"""
		pass
	def __setitem__(self, column, value):
		"""
		Set the values to the columns
		"""
		pass
	def getone(self, column = None):
		"""
		Return exactly one element.
		If the selector matches multiple rows
		the first row is choosen.

		If ``column`` is None the entired row will be returned.

		Returns ``None`` if no matching rows were found.
		"""
		pass
	def __next__(self):
		"""
		return the next matching row
		"""
		pass


class LjsonQueryResult(object):
	"""
	This is the class that is used to handle query results for LJSON.

	Until v0.2.0 query results were just lists or scalar objects 
	(returned by ``LjsonSelector.getone(column != 0)``).

	This resulted in undefined (and unwanted) behaviour in many use 
	cases, like ``table[{"some_field": some_value}]["some_field"] += another_value``.

	Therefore the LjsonQueryResult has been introduced, behaving in the most cases
	like a list (like before) but providing a new way of item assignment.

	This class should be new in v0.3.0.
	"""
	def __init__(self, table, selector, selected, list_):
		self.table = table
		self.selector = selector
		self._list = list_
		self._selected = selected

	def __iadd__(self, item):
		pass
	def __imul__(self, item):
		pass
	def __isub__(self, item):
		pass
	def __itruediv__(self, item):
		pass
	def __ifloordiv__(self, item):
		pass
	def __imod__(self, item):
		pass
	def __ipow__(self, item, modulo = None):
		pass
	def __iand__(self, item):
		pass
	def __ixor__(self, item):
		pass
	def __ior__(self, item):
		pass

	def __ilshift__(self, item):
		pass
	def __irshift__(self, item):
		pass

	def __len__(self):
		return len(self._list)
	def __next__(self):
		return self._list.__next__()
	def __add__(self, item):
		return self._list.__add__(item)
	def __radd__(self, item): 
		return self._list.__radd__(item)
	def __mul__(self, item):
		return self._list.__mul__(item)
	def __rmul__(self, item):
		return self._list.__rmul__(item)
	def __iter__(self):
		return self._list.__iter__()
	def __repr__(self):
		return self._list.__repr__()
	def __str__(self):
		return self._list.__str__()
	def __getitem__(self, item):
		return self._list.__getitem__(item)
	def __setitem__(self, name, item):
		return self._list.__setitem__(name, item)
	def __reversed__(self):
		return self._list.__reversed__()

	def __getattr__(self, name):
		if name in ("_list", "table", "selector", "_selected"):
			return object.__getattr__(self, name)
		return getattr(self._list, name)
	def __setattr__(self, name, value):
		if name in ("_list", "table", "selector", "_selected"):
			return object.__setattr__(self, name, value)
		
		return setattr(self._list, name, value)
	

def row_matches(row, dct):
	for k, v in dct.items():
		if(row[k] != v):
			return False
	return True
