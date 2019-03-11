"""
An on-disk ljson implementation.
"""

import json, os
from .generic import Header, LjsonTable, LjsonSelector,  row_matches, LjsonQueryResult
from collections import deque
from threading import RLock

class Table(LjsonTable):
	"""
	An on-disk ljson table.

	One should **not** use the constructor to open
	a file but instead use the static method from_file.

	WARNING: ``file_`` **must** be opened in ``w+`` mode!
	"""
	can_detach_after_fromfile = False

	def __init__(self, header, file_, is_headless = False):
		self._headless = is_headless
		self.header = header
		self.file = file_
		self._file_pointer_stack = deque()
		self._loop_file_pointer_stack = deque()
		self._lock = RLock()

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


	@classmethod
	def _from_file(cls, fin):
		"""
		WARNING: ``file_`` **must** be opened in ``r+`` mode!
		"""
		header, _headless = Header.from_file(fin)
		return cls(header, fin, _headless)

	def __getitem__(self, dct):
		for k in dct:
			if(not k in self.header.descriptor):
				raise KeyError("unknow key: {}".format(k))

		return Selector(self.header, dct, self)
	def __next__(self):
		with self._lock:
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
			if(not row or row.isspace()):
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
		with self._lock:
			self.file.close()
		del(self.header)
		del(self)
		return False

	def _save(self, fout):
		"""
		Save this table to the file ``fout``.
		"""
		with self._lock:
			seek = self.file.tell()
			self.file.seek(0)
			for r in self.file:
				if(r.isspace()):
					continue
				fout.write(r)
			self.file.seek(seek)
	def additem(self, row):
		"""
		Add a new row.
		"""
		with self._lock:
			seek = self.file.tell()
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
			self.file.flush()
			self.file.seek(seek)
	def __contains__(self, dct):
		with self._lock:
			seek = self.file.tell()
			self.file.seek(0)
			if(not self._headless):
				self.file.readline()
			for row in self.file:
				if(row.isspace()):
					continue
				if(row_matches(json.loads(row), dct)):
					self.file.seek(seek)
					return True
			self.file.seek(seek)
			return False
	def __iter__(self):
		with self._lock:
			self._file_pointer_stack.appendleft(self.file.tell())
			self.file.seek(0)
			if(not self._headless):
				self.file.readline()
			self._loop_file_pointer_stack.appendleft(self.file.tell())
			return self

	def __delitem__(self, dct):
		with self._lock:
			if(self._file_pointer_stack):
				raise RuntimeError("Attempt to delete item from table during looping. This leads to undefined behaviour.")
			seek_after = self.file.tell()
			max_seek = 0
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
					max_seek = buf.tell()
			self.file.close()
			self.file = buf
			self.file.flush()
			if(seek_after <= max_seek):
				self.file.seek(seek_after)
			else:
				self.file.seek(0)
				raise RuntimeWarning("File is truncated. unable to restore table state.")
			if(not deleted_row):
				raise KeyError("no matching rows found: {}".format(dct))
	def close(self):
		"""
		Close the underlaying file.
		"""
		self.file.close()
		del(self)


class Selector(LjsonSelector):
	def __init__(self, header, dct, table):
		self.header = header
		self.file = table.file
		self.dct = dct
		self.table = table
		self._file_pointer_stack = deque()
		self._loop_file_pointer_stack = deque()

	def getone(self, column = None):
		with self.table._lock:
			seek_after = self.file.tell()
			self.file.seek(0)
			if(not self.table._headless):
				self.file.readline()
			for line in self.file:
				if(line.isspace()):
					continue
				row = json.loads(line)
				if(row_matches(row, self.dct)):
					if(column):
						self.file.seek(seek_after)
						return row[column]
					else:
						self.file.seek(seek_after)
						return row
			self.file.seek(seek_after)
			return None
	def __getitem__(self, column):
		with self.table._lock:
			seek_after = self.file.tell()
			self.file.seek(0)
			if(not self.table._headless):
				self.file.readline()
			res = deque()
			for line in self.file:
				row = json.loads(line)
				if(row_matches(row, self.dct)):
					res.append(row[column])
			self.file.seek(seek_after)
			return QueryResult(self.table, self, column, list(res))

	def __setitem__(self, column, value):
		with self.table._lock:
			if(self._file_pointer_stack or self.table._file_pointer_stack):
				raise RuntimeError("Attempt to edit table while iterating")
			seek_after = self.file.tell()
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
			self.table.file.seek(seek_after)
			self.file.flush()

	def __next__(self):
		with self.table._lock:
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
			while(row.isspace() or not row_matches(data, self.dct)):
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
		with self.table._lock:
			self._file_pointer_stack.appendleft(self.file.tell())
			self.file.seek(0)
			if(not self.table._headless):
				self.file.readline()
			self._loop_file_pointer_stack.appendleft(self.file.tell())
			return self



class QueryResult(LjsonQueryResult):
	"""
	See ``ljson.base.generic.LjsonQueryResult``.
	"""
	def _perform_change(self, func, *args):
		"""
		This is used to keep the overhead of modifications at one place.
		"""
		with self.table._lock:
			if(self.selector._file_pointer_stack or self.table._file_pointer_stack):
				raise RuntimeError("Attempt to edit table while iterating")
			seek_after = self.table.file.tell()
			self.table.file.seek(0)
			os.unlink(self.table.file.name)
			buf = open(self.table.file.name, "w+")
			if(not self.table._headless):
				buf.write(self.table.file.readline())
			for line in self.table.file:
				if(line.isspace()):
					continue
				r = json.loads(line)
				if(row_matches(r, self.selector.dct)):
					r[self._selected] = func(r[self._selected], *args)
					json.dump(r, buf)
					buf.write("\n")
				else:
					buf.write(line)
			self.table.file.close()
			self.table.file = buf
			self.table.file.flush()
			self.selector.file = buf
			self.table.file.seek(seek_after)

	def __iadd__(self, item):
		self._perform_change(lambda a,b: a + b, item)
		return self
	def __imul__(self, item):
		self._perform_change(lambda a,b: a * b, item)
		return self
	def __isub__(self, item):
		self._perform_change(lambda a,b: a - b, item)
		return self
	def __itruediv__(self, item):
		self._perform_change(lambda a,b: a / b, item)
		return self
	def __ifloordiv__(self, item):
		self._perform_change(lambda a,b: a // b, item)
		return self
	def __imod__(self, item):
		self._perform_change(lambda a,b: a % b, item)
		return self
	def __ipow__(self, item, modulo = None):
		if(modulo != None):
			self._perform_change(lambda a,b, modulo: a.__pow__(b, modulo) , item, modulo)
		else:
			self._perform_change(lambda a,b: a ** b, item)
		return self
	def __iand__(self, item):
		self._perform_change(lambda a,b: a & b, item)
		return self
	def __ixor__(self, item):
		self._perform_change(lambda a,b: a ^ b, item)
		return self
	def __ior__(self, item):
		self._perform_change(lambda a,b: a | b, item)
		return self
	def __ilshift__(self, item):
		self._perform_change(lambda a,b: a << b, item)
		return self
	def __irshift__(self, item):
		self._perform_change(lambda a,b: a >> b, item)
		return self


	def __getattr__(self, name):
		if name in ("_list", "table", "selector", "_selected", "_perform_change"):
			return object.__getattr__(self, name)
		return getattr(self._list, name)
	def __setattr__(self, name, value):
		if name in ("_list", "table", "selector", "_selected", "_perform_change"):
			return object.__setattr__(self, name, value)
		
		return setattr(self._list, name, value)

