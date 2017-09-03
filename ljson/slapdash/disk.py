from .generic import SlapdashHeader, SlapdashTable, document_matches
from ..base.generic import inversed_datatypes
from collections import defaultdict, deque
import json, os




class Table(SlapdashTable):
	def __init__(self, header, file_, reread_stats = False):
		self._first_next_call = True
		self.header = header
		self.file = file_

		self._index = 0
		self.document_count = 0

		if(reread_stats):
			self.insert_stats()

		# if the file contains data there should be a header
		# => if the header is empty there shold be no documents.
		try:
			self.document_count = header.descriptor["length"]
		except KeyError:
			pass

	@staticmethod
	def open(filename):
		"""
		Equivalent to ``Table.from_file(open(filename, "r+"))``
		"""
		if(not os.path.exists(filename)):
			raise IOError("cannot open {} for reading: does not exist".format(filename))
		fin = open(filename, "r+")
		header = SlapdashHeader.from_file(fin)
		return Table(header, fin)


	@staticmethod
	def from_file(file_):
		"""
		WARNING: ``file_`` **must** be opened in ``r+`` mode!
		"""
		header = SlapdashHeader.from_file(file_)
		return Table(header, file_)

	def additem(self, document):
		self._first_next_call = True
		if(not "field_count" in self.header.descriptor):
			self.insert_stats()
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
			except KeyError as e:
				raise_key_error = True
				wrong_type = (k, v)
				
		if(raise_key_error):
			raise KeyError("Unknown datatype for field {}: {}".format(*wrong_type))

		self.document_count += 1
				
		self.header.descriptor.update({"length": self.document_count, "field_count": dict(counter),
			"total_datatype_count": dict(dtype_counter),
			"per_field_datatype_count": dict(dtype_per_field_counter)})

		self.file.seek(0, 2) # EOF here
		self.file.write("\n")
		json.dump(document, self.file)

	def __getitem__(self, dct):
		return Selector(self.header, dct, self)
	def __iter__(self):
		self._first_next_call = True
		return self
	def __contains__(self, dct):
		self._first_next_call = True
		self.file.seek(0)
		self.file.readline()
		for row in self.file:
			if(row.isspace()):
				continue
			if(document_matches(json.loads(row), dct)):
				return True
		return False
	def save(self, fout):
		"""
		Save this table to the file ``fout``.
		"""
		self._first_next_call = True
		self.file.seek(0)
		for r in self.file:
			if(r.strip == ""):
				continue
			fout.write(r)
	def __next__(self):
		if(self._first_next_call):
			self._first_next_call = False
			self.file.seek(0)
			self.file.readline()
		row = self.file.__next__()
		while(row.strip() == ""):
			row = self.file.__next__()
		return json.loads(row)

	def __enter__(self):
		return self
	def __exit__(self, exc_type, exc_value, traceback):
		self.file.close()
		del(self.header)
		del(self)
		return False


	def insert_stats(self):
		self.header.descriptor.update(self.calculate_stats())

		os.unlink(self.file.name)
		new_file = open(self.file.name, "w+")
		self.file.seek(0)
		self.file.readline()

		new_file.write(self.header.get_header())

		for line in self.file:
			if(line.isspace()):
				continue
			new_file.write(line)
		self.file.close()
		self.file = new_file

	def calculate_stats(self):
		counter = defaultdict(int)
		dtype_counter = defaultdict(int)
		dtype_per_field_counter = defaultdict()

		for doc in self:
			for k, v in doc.items():
				counter[k] += 1
				dtype_counter[inversed_datatypes[type(v)]] += 1
				if(not k in dtype_per_field_counter):
					dtype_per_field_counter[k] = defaultdict(int)
				dtype_per_field_counter[k][inversed_datatypes[type(v)]] += 1

		return {"length": self.document_count, "field_count": dict(counter),
			"total_datatype_count": dict(dtype_counter),
			"per_field_datatype_count": dict(dtype_per_field_counter)}
	def __delitem__(self, dct):
		self._first_next_call = True
		self.file.seek(0)
		os.unlink(self.file.name)
		buf = open(self.file.name, "w+")
		buf.write(self.file.readline())
		deleted_row = False
		for line in self.file:
			if(line.isspace()):
				continue
			r = json.loads(line)
			if(document_matches(r, dct)):
				deleted_row = True
			else:
				buf.write(line)
		buf.seek(0)
		self.file.close()
		self.file = buf
		if(not deleted_row):
			raise KeyError("no matching rows found: {}".format(dct))

# FIXME: add abstract base class for Selector
class Selector(object):
	def __init__(self, header, dct, table):
		self.header = header
		self.file = table.file
		self.dct = dct
		self.table = table
		self._first_next_call = True

	def getone(self, column = None):
		self._first_next_call = True
		self.file.seek(0)
		self.file.readline()
		for line in self.file:
			row = json.loads(line)
			if(document_matches(row, self.dct)):
				if(column):
					return row[column]
				else:
					return row
		return None
	def __getitem__(self, column):
		self._first_next_call = True
		self.file.seek(0)
		self.file.readline()
		res = deque()
		for line in self.file:
			row = json.loads(line)
			if(document_matches(row, self.dct)):
				res.append(row[column])
		return list(deque)
			
	def __setitem__(self, column, value):
		self._first_next_call = True
		self.file.seek(0)
		os.unlink(self.file.name)
		buf = open(self.file.name, "w+")
		buf.write(self.file.readline())
		for line in self.file:
			if(line.isspace()):
				continue
			r = json.loads(line)
			if(document_matches(r, self.dct)):
				r[column] = value
				json.dump(r, buf)
				buf.write("\n")
			else:
				buf.write(line)
		self.file.close()
		self.file = buf
		self.table.file = buf

	def __next__(self):
		if(self._first_next_call):
			self._first_next_call = False
			self.file.seek(0)
			self.file.readline()
		row = self.file.__next__()
		data = {}
		if(not row.isspace()):
			data = json.loads(row)
		while(row.isspace() or not document_matches(data, self.dct)):
			row = self.file.__next__()
			data = json.loads(row) if not row.isspace() else {}
		return data
	def __iter__(self):
		self._first_next_call = True
		return self
