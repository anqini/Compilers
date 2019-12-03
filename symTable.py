
class SymTable:
	stack = []
	def __init__(self):
		self.stack.append({})
	def __setitem__(self, key, value):
		self.stack[-1][key] = value
	def __getitem__(self, key):
		for ht in reversed(self.stack):
			if key in ht:
				return ht[key]
		raise Exception("Error: No Such Key!")
	def grow(self):
		self.stack.append({})
	def pop(self):
		if not self.stack:
			raise Exception('Error: Stack is Empty!')
		self.stack.pop()
	def print(self):
		for ht in self.stack:
			print(ht)
	def __contains__(self, key):
		for ht in reversed(self.stack):
			if key in ht:
				return True
		return False


