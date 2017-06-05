"""
An on-disk ljson implementation.
"""

import json, os
from .generic import Header, LjsonTable, LjsonSelector, UniqueLjsonSelector, row_matches
from collections import deque
from tempfile import TemporaryFile

class Table(LjsonTable):
	"""
	An on-disk ljson table.

	One should **not** use the constructor to open
	a file but instead use the static method from_file.

	WARNING: ``file_`` **must** be opened in ``w+`` mode!
	"""

	def __init__(self, header, file_):
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
		header = Header.from_file(fin)
		return Table(header, fin)


	@staticmethod
	def from_file(fin):
		"""
		WARNING: ``file_`` **must** be opened in ``r+`` mode!
		"""
		header = Header.from_file(fin)
		return Table(header, fin)

	def __getitem__(self, dct):
		for k in dct:
			if(not k in self.header.descriptor):
				raise KeyError("unknow key: {}".format(k))
		
		return Selector(self.header, dct, self)
	def __next__(self):
		if(self._first_next_call):
			self._first_next_call = False
			self.file.seek(0)
			self.file.readline()
		return json.loads(self.file.__next__())

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
				values = [r[k] for r in self.rows]
				if(v in values):
					raise ValueError("Value {} is not unique: {}".format(k, v))
		self.file.seek(0, 2) # EOF here
		self.file.write("\n")
		json.dump(row, self.file)
	def __contains__(self, dct):
		self._first_next_call = True
		self.file.seek(0)
		self.file.readline()
		for row in self.file:
			if(row.isspace()):
				continue
			if(row_matches(json.loads(row), dct)):
				return True
		return False
	def __iter__(self):
		self._first_next_call = True
		self.file.seek(0)
		self.file.readline()
		return iter([json.loads(line) for line in self.file])
	def __list__(self):
		self._first_next_call = True
		self.file.seek(0)
		self.file.readline()
		return [json.loads(line) for line in self.file]


	
class Selector(LjsonSelector):
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
			if(row_matches(row, self.dct)):
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
			if(row_matches(row, self.dct)):
				res.append(row[column])
		return list(deque)
			
	def __setitem__(self, column, value):
		self._first_next_call = True
		self.file.seek(0)
		buf = TemporaryFile(mode = "w+")
		buf.write(self.file.readline())
		for line in self.file:
			r = json.loads(line)
			if(row_matches(r, self.dct)):
				r[column] = value
				json.dump(r, buf)
				buf.write("\n")
			else:
				buf.write(line)
		buf.seek(0)
		self.file.truncate(0)
		self.file.seek(0)
		for line in buf:
			self.file.write(line)
		buf.close()

	def __next__(self):
		if(self._first_next_call):
			self._first_next_call = False
			self.file.seek(0)
			self.file.readline()
		return json.loads(self.file.__next__())
	def __iter__(self):
		self._first_next_call = True
		self.file.seek(0)
		self.file.readline()
		
		res = deque()
		
		for line in self.file:
			row = json.loads(line)
			if(row_matches(row, self.dct)):
				res.append(row)

		return iter(res)
	def __list__(self):
		self._first_next_call = True
		self.file.seek(0)
		self.file.readline()
		res = deque()
		
		for line in self.file:
			row = json.loads(line)
			if(row_matches(row, self.dct)):
				res.append(row)

		return list(res)
	


