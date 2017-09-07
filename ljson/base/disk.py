"""
An on-disk ljson implementation.
"""

import json, os
from .generic import Header, LjsonTable, LjsonSelector,  row_matches
from collections import deque

class Table(LjsonTable):
	"""
	An on-disk ljson table.

	One should **not** use the constructor to open
	a file but instead use the static method from_file.

	WARNING: ``file_`` **must** be opened in ``w+`` mode!
	"""

	def __init__(self, header, file_, is_headless = False):
		self._headless = is_headless
		self.header = header
		self.file = file_
		self._first_next_call = True

	@staticmethod
	def open(filename):
		"""
		Equivalent to ``Table.from_file(open(filename, "r+"))``
		"""
		if(not os.path.exists(filename)):
			raise IOError("cannot open {} for reading: does not exist".format(filename))
		fin = open(filename, "r+")
		header, _headless = Header.from_file(fin)
		return Table(header, fin, _headless)


	@staticmethod
	def from_file(fin):
		"""
		WARNING: ``file_`` **must** be opened in ``r+`` mode!
		"""
		header, _headless = Header.from_file(fin)
		return Table(header, fin, _headless)

	def __getitem__(self, dct):
		for k in dct:
			if(not k in self.header.descriptor):
				raise KeyError("unknow key: {}".format(k))

		return Selector(self.header, dct, self)
	def __next__(self):
		if(self._first_next_call):
			self._first_next_call = False
			self.file.seek(0)
			if(not self._headless):
				self.file.readline()
		row = self.file.__next__()
		while(row.isspace()):
			row = self.file.__next__()
		return json.loads(row)

	def __enter__(self):
		return self
	def __exit__(self, exc_type, exc_value, traceback):
		self.file.close()
		del(self.header)
		del(self)
		return False

	def save(self, fout):
		"""
		Save this table to the file ``fout``.
		"""
		self._first_next_call = True
		self.file.seek(0)
		for r in self.file:
			if(r.isspace()):
				continue
			fout.write(r)
	def additem(self, row):
		"""
		Add a new row.
		"""
		self._first_next_call = True
		for k, v in row.items():
			self.header.check_data(k, v)
			if("unique" in self.header.descriptor[k]["modifiers"]):
				# check if the value is unique
				for r in self:
					if(v == r[k]):
						raise ValueError("Value {} is not unique: {}".format(k, v))
		self.file.seek(0, 2) # EOF here
		self.file.write("\n")
		json.dump(row, self.file)
	def __contains__(self, dct):
		self._first_next_call = True
		self.file.seek(0)
		if(not self._headless):
			self.file.readline()
		for row in self.file:
			if(row.isspace()):
				continue
			if(row_matches(json.loads(row), dct)):
				return True
		return False
	def __iter__(self):
		self._first_next_call = True
		return self

	def __delitem__(self, dct):
		self._first_next_call = True
		self.file.seek(0)
		os.unlink(self.file.name)
		buf = open(self.file.name, "w+")
		if(not self._headless):
			buf.write(self.file.readline())
		deleted_row = False
		for line in self.file:
			if(line.isspace()):
				continue
			r = json.loads(line)
			if(row_matches(r, dct)):
				deleted_row = True
			else:
				buf.write(line)
		buf.seek(0)
		self.file.close()
		self.file = buf
		if(not deleted_row):
			raise KeyError("no matching rows found: {}".format(dct))


class Selector(LjsonSelector):
	def __init__(self, header, dct, table):
		self.header = header
		self.file = table.file
		self.dct = dct
		self.table = table
		self._first_next_call = True

	def getone(self, column = None):
		self.table._first_next_call = True
		self._first_next_call = True
		self.file.seek(0)
		if(not self.table._headless):
			self.file.readline()
		for line in self.file:
			if(line.isspace()):
				continue
			row = json.loads(line)
			if(row_matches(row, self.dct)):
				if(column):
					return row[column]
				else:
					return row
		return None
	def __getitem__(self, column):
		self._first_next_call = True
		self.table._first_next_call = True
		self.file.seek(0)
		if(not self.table._headless):
			self.file.readline()
		res = deque()
		for line in self.file:
			row = json.loads(line)
			if(row_matches(row, self.dct)):
				res.append(row[column])
		return list(res)

	def __setitem__(self, column, value):
		self._first_next_call = True
		self.table._first_next_call = True
		self.file.seek(0)
		os.unlink(self.file.name)
		buf = open(self.file.name, "w+")
		if(not self.table._headless):
			buf.write(self.file.readline())
		for line in self.file:
			if(line.isspace()):
				continue
			r = json.loads(line)
			if(row_matches(r, self.dct)):
				r[column] = value
				json.dump(r, buf)
				buf.write("\n")
			else:
				buf.write(line)
		self.file.close()
		self.file = buf
		self.table.file = buf

	def __next__(self):
		self.table._first_next_call = True
		if(self._first_next_call):
			self._first_next_call = False
			self.file.seek(0)
			if(not self.table._headless):
				self.file.readline()
		row = self.file.__next__()
		data = {}
		if(not row.isspace()):
			data = json.loads(row)
		while(row.isspace() or not row_matches(data, self.dct)):
			row = self.file.__next__()
			data = json.loads(row) if not row.isspace() else {}
		return data
	def __iter__(self):
		self.table._first_next_call = True
		self._first_next_call = True
		return self




