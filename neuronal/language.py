# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import re

def tokenize(text):
	r = re.compile(r'[^a-zäöüß]')
	process = lambda x: r.sub(' ', x.lower())
	text = process(text)
	tokens = [ x.strip() for x in text.split(" ") if len(x.strip()) != 0 ]
	return tokens

def parse(text):
	tokens = tokenize(text)
	result = []
	for token in tokens:
		if not token in result:
			result += [ token ]
	return result

def synthesize(tokens):
	return " ".join(tokens)

class Language(object):
	def __init__(self, words = [], synonyms = []):
		self.words = words
		self.synonyms = synonyms

	def load(self, filename):
		with open(filename) as f:
			self.words = [ x.strip() for x in f.readlines() ]

	def load_synonyms(self, filename):
		self.synonyms = []
		with open(filename) as f:
			for line in f:
				line = line.strip()
				if len(line) == 0:
					continue
				if line[0] == '#':
					continue
				tokens = [ x.strip() for x in line.split(";") \
						if len(x.strip()) > 0 ]
				self.synonyms += [ tokens ]


	def dump(self):
		print(self.words)

	def map(self, word):
		return self.words.index(self.base(word))

	def unmap(self, index):
		return self.words[index]

	def has(self, text):
		if text in self.words:
			return True
		for s in self.synonyms:
			if text in s:
				return True
		return False

	def base(self, word):
		for s in self.synonyms:
			if word in s:
				return s[0]
		return word

	def parse(self, text):
		thought = parse(text)
		data = [ self.map(x) for x in thought if self.has(x) ]
		#if len(thought) != len(data):
		#	print("'%s' => '%s'" % (text, self.synthesize(data)))
		if float(len(data)) / float(len(thought)) < 0.66:
			raise Exception('i did not understand: "%s" -> %s' \
					% (text, self.synthesize(data)))
		return data

	def synthesize(self, thought):
		return " ".join([ self.unmap(x) for x in thought ])

	def __getitem__(self, index):
		if type(index) == str:
			return self.map(index)
		return self.unmap(index)

	def __len__(self):
		return len(self.words)

class Pattern(object):
	def __init__(self, value):
		self.value = value
		self.children = []

	def __equals__(self, value):
		return self.value == value

	def append(self, child):
		self.children += [ child ]
