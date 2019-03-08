"""
An in-memory ljson implementation.

This module might be used if the entired set is
needed or the set is small.
"""

import json, os, collections
from .generic import Header, LjsonTable, LjsonSelector, row_matches, LjsonQueryResult

class Table(LjsonTable):
	"""
	A memory ljson table.

	One should **not** use the constructor to open
	a file but instead use the static method from_file.
	"""
	def __init__(self, header, rows):
		self.header = header
		self.rows = rows
		self._index = 0 # used by __next__

	@classmethod
	def _from_file(cls, fin):
		header, headless = Header.from_file(fin)
		rows = [json.loads(line) for line in fin if not line.isspace()]
		return cls(header, rows)
	@staticmethod
	def open(filename):
		"""
		Equivalent to ``Table.from_file(open(filename, "r"))``
		"""
		if(not os.path.exists(filename)):
			raise IOError("cannot open {} for reading: does not exist".format(filename))
		fin = open(filename, "r")
		table = Table.from_file(fin)

		fin.close()
		return table

	def __enter__(self):
		return self
	def __exit__(self, exc_type, exc_value, traceback):
		return False

	def __repr__(self):
		return "{mymod}.{mytype}({header}, {table})".format(mytype = type(self).__name__,
				mymod = type(self).__module__,
				header = repr(self.header),
				descriptor = self.header.descriptor,
				table = self.rows)

	def __getitem__(self, dct):
		for k in dct:
			if(not k in self.header.descriptor):
				raise KeyError("unknow key: {}".format(k))

		return Selector(self.header, dct, self)

	def __next__(self):
		if(self._index >= len(self.rows)):
			raise StopIteration()

		res = self.rows[self._index]
		self._index += 1
		return res
	def _save(self, fout):
		fout.write(self.header.get_header())
		for r in self.rows:
			fout.write("\n")
			json.dump(r, fout)

	def additem(self, row):
		for k, v in row.items():
			self.header.check_data(k, v)
			if("unique" in self.header.descriptor[k]["modifiers"]):
				# check if the value is unique
				values = [r[k] for r in self.rows]
				if(v in values):
					raise ValueError("Value {} is not unique: {}".format(k, v))
		self.rows.append(row)
	def __contains__(self, dct):
		for row in self.rows:
			if(row_matches(row, dct)):
				return True
		return False
	def __iter__(self):
		self._index = 0
		return self
	def __delitem__(self, dct):
		que = collections.deque()
		for i, row in enumerate(self.rows):
			if(row_matches(row, dct)):
				que.appendleft(i)
		if(not len(que)):
			raise KeyError("no matching rows found: {}".format(dct))
		for i in que:
			del(self.rows[i])




class Selector(LjsonSelector):
	def __init__(self, header, dct, table):
		self.header = header
		self.rows = [r for r in table.rows if row_matches(r, dct)]
		self.dct = dct
		self.table = table
		self._index = 0

	def getone(self, column = None):
		if(not len(self.rows)):
			return None
		if(column != None):
			return self.rows[0][column]
		else:
			return self.rows[0]
	def __getitem__(self, column):
		return QueryResult(self.table, self, column, [row[column] for row in self.rows])
	def __setitem__(self, column, value):
		# FIXME: maybe one should make this more memory efficient.
		# I am pretty sure that the rows do not get copied, so
		# setitem should be usable.
		rows = self.table.rows
		for r in self.table.rows:
			if(row_matches(r, self.dct)):
				r[column] = value
		self.table.rows = rows
	def __next__(self):
		if(self._index >= len(self.rows)):
			raise StopIteration()
		res = self.rows[self._index]
		self._index += 1
		return res
	def __iter__(self):
		self._index = 0
		return self


class QueryResult(LjsonQueryResult):
	"""
	See ``ljson.base.generic.LjsonQueryResult``.
	"""
	def __iadd__(self, item):
		for row in self.selector.rows:
			row[self._selected] += item
		return self
	def __imul__(self, item):
		for row in self.selector.rows:
			row[self._selected] *= item
		return self
	def __isub__(self, item):
		for row in self.selector.rows:
			row[self._selected] -= item
		return self
	def __itruediv__(self, item):
		for row in self.selector.rows:
			row[self._selected] /= item
		return self
	def __ifloordiv__(self, item):
		for row in self.selector.rows:
			row[self._selected] //= item
		return self
	def __imod__(self, item):
		for row in self.selector.rows:
			row[self._selected] %= item
		return self
	def __ipow__(self, item, modulo = None):
		if(modulo != None):
			for row in self.selector.rows:
				row[self._selected] = row[self._selected].__pow__(item, modulo)
		else:
			for row in self.selector.rows:
				row[self._selected] = row[self._selected].__pow__(item)
		return self
	def __iand__(self, item):
		for row in self.selector.rows:
			row[self._selected] &= item
		return self
	def __ixor__(self, item):
		for row in self.selector.rows:
			row[self._selected] ^= item
		return self
	def __ior__(self, item):
		for row in self.selector.rows:
			row[self._selected] |= item
		return self


	def __ilshift__(self, item):
		for row in self.selector.rows:
			row[self._selected] <<= item
		return self
	def __irshift__(self, item):
		for row in self.selector.rows:
			row[self._selected] >>= item
		return self
