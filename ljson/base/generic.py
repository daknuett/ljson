"""
Some generic functions and classes for ljson.

They are used by the memory and the disk implementation.
"""
import json

datatypes = (int, str, float, bool, bytes, dict, list)

datatype_by_name = {"int": int, "str": str, "float": float, "bytes": bytes, "bool": bool, "json": json.loads}
python_datatype_by_name = {"int": int, "str": str, "float": float, "bytes": bytes, "bool": bool, "json": (list, dict)}

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
		data = json.loads(line)
		if(not "__type__" in data or data["__type__"] != "header"):
			fin.seek(0)
			descriptor = {}
			for k, v in data.items():
				descriptor[k] = {"type": None, "modifiers": []}
			return Header(descriptor)
		del(data["__type__"])
		return Header(data)

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


class LjsonSelector(object):
	def __init__(self):
		pass
	def __getitem__(self, column):
		"""
		Return the column values as a list of lists
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

class UniqueLjsonSelector(object):
	"""
	This selector can be used if the rows are unique.
	"""
	def __init__(self):
		pass
	def __getitem__(self, column):
		"""
		Return the value of ``column``
		"""
		pass
	def __setitem__(self, column, value):
		"""
		Set the value of the column.
		"""
		pass

def row_matches(row, dct):
	for k, v in dct.items():
		if(row[k] != v):
			return False
	return True
