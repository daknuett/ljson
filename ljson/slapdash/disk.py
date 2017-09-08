from .generic import SlapdashHeader, SlapdashTable, document_matches
from ..base.generic import inversed_datatypes
from collections import defaultdict, deque
import json, os




class Table(SlapdashTable):
	def __init__(self, header, file_, reread_stats = False):
		self.header = header
		self.file = file_

		self._index = 0
		self.document_count = 0

		self._file_pointer_stack = deque()
		self._loop_file_pointer_stack = deque()

		if(reread_stats):
			self.insert_stats()

		# if the file contains data there should be a header
		# => if the header is empty there shold be no documents.
		try:
			self.document_count = header.descriptor["length"]
		except KeyError:
			pass

	


	@classmethod
	def empty(cls, file_or_filename):
		"""
		Create a new empty table with the given file
		or filename.
		"""

		header = SlapdashHeader({})
		
		if(isinstance(file_or_filename, str)):
			file_ = open(file_or_filename, "w+")
		else:
			file_ = file_or_filename

		file_.write(header.get_header())
		table = cls(header, file_)

		table.insert_stats()

		return table



	@staticmethod
	def from_file(file_):
		"""
		WARNING: ``file_`` **must** be opened in ``r+`` mode!
		"""
		header = SlapdashHeader.from_file(file_)
		return Table(header, file_)

	def additem(self, document):
		seek_after = self.file.tell()
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
			except KeyError:
				raise_key_error = True
				wrong_type = (k, v)

		if(raise_key_error):
			self.file.seek(seek_after)
			raise KeyError("Unknown datatype for field {}: {}".format(*wrong_type))

		self.document_count += 1

		self.header.descriptor.update({"length": self.document_count, "field_count": dict(counter),
			"total_datatype_count": dict(dtype_counter),
			"per_field_datatype_count": dict(dtype_per_field_counter)})

		self.file.seek(0, 2) # EOF here
		self.file.write("\n")
		json.dump(document, self.file)
		self.file.seek(seek_after)

	def __getitem__(self, dct):
		return Selector(self.header, dct, self)
	def __iter__(self):
		self._file_pointer_stack.appendleft(self.file.tell())
		self.file.seek(0)
		self.file.readline()
		self._loop_file_pointer_stack.appendleft(self.file.tell())
		return self
	def __contains__(self, dct):
		seek_after = self.file.tell()
		self.file.seek(0)
		self.file.readline()
		for row in self.file:
			if(row.isspace()):
				continue
			if(document_matches(json.loads(row), dct)):
				self.file.seek(seek_after)
				return True
		self.file.seek(seek_after)
		return False
	def save(self, fout):
		"""
		Save this table to the file ``fout``.
		"""
		seek_after = self.file.tell()
		self.file.seek(0)
		for r in self.file:
			if(r.strip == ""):
				continue
			fout.write(r)
		self.file.seek(seek_after)
	def __next__(self):
		seek_after = self.file.tell()
		self.file.seek(self._loop_file_pointer_stack.popleft())


		row = self.file.readline()
		if(not row):
			# we are leaving the loop => this context is done
			# => return to the context before __iter__ was called
			self.file.seek(self._file_pointer_stack.popleft())
			raise StopIteration()
		while(row.isspace()):
			row = self.file.readline()
		if(not row):
			# we are leaving the loop => this context is done
			# => return to the context before __iter__ was called
			self.file.seek(self._file_pointer_stack.popleft())
			raise StopIteration()
		self._loop_file_pointer_stack.appendleft(self.file.tell())
		self.file.seek(seek_after)
		return json.loads(row)

	def __enter__(self):
		return self
	def __exit__(self, exc_type, exc_value, traceback):
		self.file.close()
		del(self.header)
		del(self)
		return False


	def insert_stats(self):
		seek_after = self.file.tell()
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
		self.file.seek(seek_after)


	def calculate_stats(self):
		seek_after = self.file.tell()
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

		self.file.seek(seek_after)
		return {"length": self.document_count, "field_count": dict(counter),
			"total_datatype_count": dict(dtype_counter),
			"per_field_datatype_count": dict(dtype_per_field_counter)}
	def __delitem__(self, dct):
		if(self._file_pointer_stack):
			raise RuntimeError("Attempt to delete item from table during looping. This leads to undefined behaviour.")
		seek_after = self.file.tell()
		max_seek = 0

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
				self.document_count -= 1
			else:
				buf.write(line)
				max_seek = buf.tell()
		buf.seek(0)
		self.file.close()
		self.file = buf
		if(seek_after <= max_seek):
			self.file.seek(seek_after)
		else:
			self.file.seek(0)
			raise RuntimeWarning("File is truncated. unable to restore table state.")
		if(not deleted_row):
			raise KeyError("no matching rows found: {}".format(dct))

# FIXME: add abstract base class for Selector
class Selector(object):
	def __init__(self, header, dct, table):
		self.header = header
		self.file = table.file
		self.dct = dct
		self.table = table
		self._file_pointer_stack = deque()
		self._loop_file_pointer_stack = deque()

	def getone(self, column = None):
		seek_after = self.file.tell()
		self.file.seek(0)
		self.file.readline()
		for line in self.file:
			row = json.loads(line)
			if(document_matches(row, self.dct)):
				if(column):
					self.file.seek(seek_after)
					return row[column]
				else:
					self.file.seek(seek_after)
					return row
		self.file.seek(seek_after)
		return None
	def __getitem__(self, column):
		seek_after = self.file.tell()
		self.file.seek(0)
		self.file.readline()
		res = deque()
		for line in self.file:
			row = json.loads(line)
			if(document_matches(row, self.dct)):
				res.append(row[column])
		self.file.seek(seek_after)
		return list(res)

	def __setitem__(self, column, value):
		if(self._file_pointer_stack or self.table._file_pointer_stack):
			raise RuntimeError("Attempt to edit table while iterating")
		seek_after = self.file.tell()
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
		self.table.file.seek(seek_after)

	def __next__(self):
		seek_after = self.file.tell()
		self.file.seek(self._loop_file_pointer_stack.popleft())


		row = self.file.readline()
		if(not row):
			# we are leaving the loop => this context is done
			# => return to the context before __iter__ was called
			self.file.seek(self._file_pointer_stack.popleft())
			raise StopIteration()
		data = {}
		if(not row.isspace()):
			data = json.loads(row)
		while(row.isspace() or not document_matches(data, self.dct)):
			row = self.file.readline()
			if(not row):
				# we are leaving the loop => this context is done
				# => return to the context before __iter__ was called
				self.file.seek(self._file_pointer_stack.popleft())
				raise StopIteration()
			data = json.loads(row) if not row.isspace() else {}
		self._loop_file_pointer_stack.appendleft(self.file.tell())
		self.table.file.seek(seek_after)
		return data
	def __iter__(self):
		self._file_pointer_stack.appendleft(self.file.tell())
		self.file.seek(0)
		self.file.readline()
		self._loop_file_pointer_stack.appendleft(self.file.tell())
		return self
