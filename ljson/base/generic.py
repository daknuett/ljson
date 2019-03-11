"""
Some generic functions and classes for ljson.

They are used by the memory and the disk implementation.
"""
import json
import io
import abc
from abc import abstractmethod

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

	@classmethod
	def from_file(cls, fin):
		"""
		Construct the header from the file.
		"""
		detach = False
		if(not isinstance(fin, (io.StringIO, io.TextIOBase))):
			fin = io.TextIOWrapper(fin)
			detach = True

		line = fin.readline()
		print(type(fin), line)
		while(line.isspace()):
			line = fin.readline()
		data = json.loads(line)
		if(not "__type__" in data or data["__type__"] != "header"):
			fin.seek(0)
			descriptor = {}
			for k in data.keys():
				descriptor[k] = {"type": None, "modifiers": []}
			return cls(descriptor), True
		del(data["__type__"])

		if(detach):
			fin.detach()

		return cls(data), False

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


class LjsonTable(metaclass=abc.ABCMeta):
	can_detach_after_fromfile = True
	def __init__(self):
		self.header = None
	@abstractmethod
	def _save(self, fout):
		"""
		Save the table to the given file.
		"""
		pass
	def save(self, fout):
		detach = False
		if(not isinstance(fout, (io.TextIOBase, io.StringIO, io.TextIOWrapper))):
			fout = io.TextIOWrapper(fout)
			detach = True
		result = self._save(fout)
		if(detach):
			fout.detach()
		return result



	@abstractmethod
	def __getitem__(self, dct):
		"""
		Select rows by the dict dct.
		Returns a LjsonSelector object.

		Using dict as index is required to provide
		"search functionality".

		See also the ljson.base documentation.
		"""
		pass
	@abstractmethod
	def __next__(self):
		"""
		Returns: the next row of the table
		"""
		pass
	@classmethod
	def from_file(cls, fin):
		"""
		Construct the table from the given file.
		"""
		detach = False
		if(not isinstance(fin, (io.StringIO, io.TextIOWrapper, io.TextIOBase))):
			fin = io.TextIOWrapper(fin)
			detach = True
		result = cls._from_file(fin)
		if(detach and cls.can_detach_after_fromfile):
			fin.detach()
		return result
	@abc.abstractclassmethod
	def _from_file(cls, fin):
		pass

	@staticmethod
	def open(filename):
		"""
		Equivalent to ``Table.from_file(open(filename, "r+"))``
		"""
		pass
	@abstractmethod
	def additem(self, row):
		"""
		Add the row to the table.
		"""
	@abstractmethod
	def __contains__(self, dct):
		"""
		Check if there is at least one row matching the selector ``dct``

		Example::

			{"id": 4} in table
		"""
		pass
	@abstractmethod
	def __delitem__(self, dct):
		"""
		Delete all matching items.
		"""
		pass

	def close(self):
		"""
		This is only used in ``ljson.base.disk`` and just for compability here.
		"""
		pass


class LjsonSelector(metaclass=abc.ABCMeta):
	def __init__(self):
		pass
	@abstractmethod
	def __getitem__(self, column):
		"""
		Return the column values as a list
		"""
		pass
	@abstractmethod
	def __setitem__(self, column, value):
		"""
		Set the values to the columns
		"""
		pass
	@abstractmethod
	def getone(self, column = None):
		"""
		Return exactly one element.
		If the selector matches multiple rows
		the first row is choosen.

		If ``column`` is None the entired row will be returned.

		Returns ``None`` if no matching rows were found.
		"""
		pass
	@abstractmethod
	def __next__(self):
		"""
		return the next matching row
		"""
		pass


class LjsonQueryResult(metaclass=abc.ABCMeta):
	"""
	This is the class that is used to handle query results for LJSON.

	Until v0.2.0 query results were just lists or scalar objects 
	(returned by ``LjsonSelector.getone(column != 0)``).

	This resulted in undefined (and unwanted) behaviour in many use 
	cases, like ``table[{"some_field": some_value}]["some_field"] += another_value``.

	Therefore the LjsonQueryResult has been introduced, behaving in the most cases
	like a list (like before) but providing a new way of item assignment.

	This class should be new in v0.3.0.

	***Warning***:

	| This class will behave most propably differently from what one would expect:
	| Only ``__i*__`` methods are overwritten!
	| All other methods are mapped to the underlaying ``list`` representation.
	| This leads to the fact that
	  
	::

		table[{"some_field": some_value}][some_value] += another_value
		# and
		table[{"some_field": some_value}][some_value] = another_value + table[{"some_field": some_value}][some_value]

	Are not the same!

	In particular: The first sample will produce a valid result and modify the table,
	while the latter leads to undefined behaviour.

	***FIXME***:

	There should a method ``LjsonTable.apply(selector, func, args)`` that bypasses the problem!

	
	"""
	def __init__(self, table, selector, selected, list_):
		self.table = table
		self.selector = selector
		self._list = list_
		self._selected = selected

	@abstractmethod
	def __iadd__(self, item):
		pass
	@abstractmethod
	def __imul__(self, item):
		pass
	@abstractmethod
	def __isub__(self, item):
		pass
	@abstractmethod
	def __itruediv__(self, item):
		pass
	@abstractmethod
	def __ifloordiv__(self, item):
		pass
	@abstractmethod
	def __imod__(self, item):
		pass
	@abstractmethod
	def __ipow__(self, item, modulo = None):
		pass
	@abstractmethod
	def __iand__(self, item):
		pass
	@abstractmethod
	def __ixor__(self, item):
		pass
	@abstractmethod
	def __ior__(self, item):
		pass

	@abstractmethod
	def __ilshift__(self, item):
		pass
	@abstractmethod
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
	def __eq__(self, other):
		return self._list.__eq__(other)
	def __le__(self, other):
		return self._list.__le__(other)
	def __ge__(self, other):
		return self._list.__ge__(other)
	def __lt__(self, other):
		return self._list.__lt__(other)
	def __gt__(self, other):
		return self._list.__gt__(other)

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
