"""
Some generic functions and classes for ljson.slapdash.

"""

from ..base.generic import python_datatype_by_name
import json, os

class SlapdashHeader(object):
	"""
	A Header for ljson slapdash tables.
	Used to describe the table (as good as possible).
	"""
	def __init__(self, descriptor):
		self.descriptor = descriptor
		if("__type__" in self.descriptor):
			del(self.descriptor["__type__"])
	def __repr__(self):
		return "{mymod}.{myname}({descriptor})".format(mymod = type(self).__module__,
				myname = type(self).__name__,
				descriptor = self.descriptor)
	def get_header(self):
		"""
		Return a JSON header.
		"""
		header = self.descriptor
		header["__type__"] = "slapdash-header"

		return json.dumps(header)

	@staticmethod
	def from_file(fin):
		"""
		Construct the header from the file.
		"""
		line = fin.readline()
		data = json.loads(line)
		if(not "__type__" in data or data["__type__"] != "slapdash-header"):
			return SlapdashHeader({})
		del(data["__type__"])
		return SlapdashHeader(data)


class SlapdashTable(object):
	"""
	A messy table.

	SlapdashTable is used to store inhomogenous
	data, like in a document-oriented database.
	"""
	def __getitem__(self, dct):
		pass
	def __delitem__(self, dct):
		pass
	def __next__(self):
		pass
	def __iter__(self):
		pass
	def __contains__(self, dct):
		pass
	def calculate_stats(self):
		"""
		Calculate statistical information about the
		data structure.
		Returns a dict::

			{
				"length": int,
				"field_count": dict,
				"total_datatype_count": dict,
				"per_field_datatype_count": dict
			}
		"""
		pass
	def insert_stats(self):
		"""
		Calculate statistical information about the
		data structure and store the gathered information
		in the Header.
		"""
		pass

	@staticmethod
	def from_file(file_):
		"""
		Read a SlapdashTable from a file
		"""
		pass
	def split(self, ignore = None):
		"""
		Split the table into tables containing exactly one document
		type.

		**Warning**: If the table highly inhomogenous, this will
		produce a high number of tables.

		Attribute names listed in ``ignore`` will be ignored by the split
		process and the data will not appear in the resulting tables.

		**Warning**: Currently not implemented.
		"""
		#ignore = ignore if ignore else []
		pass
	def additem(self, document):
		"""
		Add a document to the table.

		This will update the header according to the inserted document.
		"""
		pass
	def save(self, fout):
		pass

	@classmethod
	def empty(cls):
		"""
		Return a new empty slapdash table.
		"""
		pass
	@classmethod
	def open(cls, filename):
		"""
		Equivalent to ``Table.from_file(open(filename, "r+"))``
		"""
		if(not os.path.exists(filename)):
			raise IOError("cannot open {} for reading: does not exist".format(filename))
		fin = open(filename, "r+")
		return cls.from_file(fin)

def document_matches(document, dct):
	"""
	Return True, if the document matches the
	given dict. If a value in the dict is not contained
	in the document, this will return false.
	"""
	for k, v in dct.items():
		if(k in document and document[k] == v):
			continue
		else:
			return False
	return True
