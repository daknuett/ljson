#!/usr/bin/python3

from .generic import SlapdashTable, SlapdashHeader, document_matches
from ..base.generic import inversed_datatypes
from collections import defaultdict, deque
import json



class Table(SlapdashTable):
	def __init__(self, header, documents):
		self.header = header
		self.documents = documents

		self.document_count = len(documents)
		self.insert_stats()
		self._index = 0

	@classmethod
	def empty(cls):
		header = SlapdashHeader({})
		table = cls(header, [])
		return table

	@staticmethod
	def from_file(file_):

		header = SlapdashHeader.from_file(file_)

		table = Table(header, [json.loads(line) for line in file_ if not line.isspace()])
		return table


	def calculate_stats(self):
		counter = defaultdict(int)
		dtype_counter = defaultdict(int)
		dtype_per_field_counter = defaultdict()

		for doc in self.documents:
			for k, v in doc.items():
				counter[k] += 1
				dtype_counter[inversed_datatypes[type(v)]] += 1
				if(not k in dtype_per_field_counter):
					dtype_per_field_counter[k] = defaultdict(int)
				dtype_per_field_counter[k][inversed_datatypes[type(v)]] += 1

		return {"length": self.document_count, "field_count": dict(counter),
			"total_datatype_count": dict(dtype_counter),
			"per_field_datatype_count": dict(dtype_per_field_counter)}

	def insert_stats(self):
		self.header.descriptor.update(self.calculate_stats())

	def additem(self, document):
		old_data = {k: self.header.descriptor[k]
			for k in ("field_count", "total_datatype_count", "per_field_datatype_count")}

		counter = defaultdict(int)
		dtype_counter = defaultdict(int)
		dtype_per_field_counter = defaultdict()

		counter.update(old_data["field_count"])
		dtype_counter.update(old_data["total_datatype_count"])
		dtype_per_field_counter.update(old_data["per_field_datatype_count"])

		raise_key_error = False
		wrong_type = None

		for k, v in document.items():
			counter[k] += 1
			try:
				dtype_counter[inversed_datatypes[type(v)]] += 1
				if(not k in dtype_per_field_counter):
					dtype_per_field_counter[k] = defaultdict(int)
				dtype_per_field_counter[k][inversed_datatypes[type(v)]] += 1
			except KeyError:
				raise_key_error = True
				wrong_type = (k, v)

		if(raise_key_error):
			raise KeyError("Unknown datatype for field {}: {}".format(*wrong_type))

		self.document_count += 1

		self.header.descriptor.update({"length": self.document_count, "field_count": dict(counter),
			"total_datatype_count": dict(dtype_counter),
			"per_field_datatype_count": dict(dtype_per_field_counter)})

		self.documents.append(document)

	def __delitem__(self, dct):
		que = deque()
		for i, document in enumerate(self.documents):
			if(document_matches(document, dct)):
				que.appendleft(i)
				self.document_count -= 1
		if(not len(que)):
			raise KeyError("no matching documents found: {}".format(dct))
		for i in que:
			del(self.documents[i])

	def __next__(self):
		if(self._index >= self.document_count):
			raise StopIteration()

		res = self.documents[self._index]
		self._index += 1
		return res

	def __contains__(self, dct):
		for document in self.documents:
			if(document_matches(document, dct)):
				return True
		return False
	def __enter__(self):
		return self
	def __exit__(self, exc_type, exc_value, traceback):
		return False

	def __repr__(self):
		return "{mymod}.{mytype}({header}, {table})".format(mytype = type(self).__name__,
				mymod = type(self).__module__,
				header = repr(self.header),
				descriptor = self.header.descriptor,
				table = self.documents)
	def save(self, fout):
		fout.write(self.header.get_header())
		for r in self.documents:
			fout.write("\n")
			json.dump(r, fout)

	def __getitem__(self, dct):
		return Selector(self.header, dct, self)
	def __iter__(self):
		self._index = 0
		return self

# FIXME: add abstract base class for Selector
class Selector(object):
	def __init__(self, header, dct, table):
		self.header = header
		self.documents = [r for r in table.documents if document_matches(r, dct)]
		self.dct = dct
		self.table = table
		self._index = 0

	def getone(self, column = None):
		if(not len(self.documents)):
			return None
		if(column != None):
			return self.documents[0][column]
		else:
			return self.documents[0]
	def __getitem__(self, column):
		return [document[column] for document in self.documents]
	def __setitem__(self, column, value):
		for i, r in enumerate(self.table.documents):
			if(document_matches(r, self.dct)):
				r[column] = value
				self.table.documents[i] = r
	def __next__(self):
		if(self._index >= len(self.documents)):
			raise StopIteration()
		res = self.documents[self._index]
		self._index += 1
		return res
	def __iter__(self):
		self._index = 0
		return self

