# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from pybrain.tools.shortcuts import buildNetwork
#from pybrain.structure import FeedForwardNetwork, FullConnection, LinearLayer, SigmoidLayer, TanhLayer, SoftmaxLayer
from pybrain.structure import SigmoidLayer
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
import pickle
#import functools

#from pybrain.tools.xml.networkreader import NetworkReader, NetworkWriter

class Brain(object):
	def __init__(self, lang, thoughts, messages, error = 0.002):
		self.error = error
		self.lang = lang
		self.thoughts = thoughts
		self.messages = messages
		word_count = len(lang)
		thought_count = len(thoughts)
		self.translate = Translate(thoughts, messages)
		self.nn = buildNetwork(word_count, 4 * word_count,
				thought_count, bias=True,
				hiddenclass=SigmoidLayer)
		#in_layer = LinearLayer(words)
		#hidden_layer_01 = SigmoidLayer(int(1.5 * words))
		#hidden_layer_02 = SigmoidLayer(int(1.5 * words))
		#hidden_layer_03 = SigmoidLayer(int(1.5 * words))
		#hidden_layer_04 = SigmoidLayer(words)
		#out_layer = LinearLayer(len(thoughts))
		#self.nn = FeedForwardNetwork()
		#self.nn.addInputModule(in_layer)
		#self.nn.addModule(hidden_layer_01)
		#self.nn.addModule(hidden_layer_02)
		#self.nn.addModule(hidden_layer_03)
		#self.nn.addModule(hidden_layer_04)
		#self.nn.addOutputModule(out_layer)
		#connection_01 = FullConnection(in_layer, hidden_layer_01)
		#connection_02 = FullConnection(hidden_layer_01, hidden_layer_02)
		#connection_03 = FullConnection(hidden_layer_02, hidden_layer_03)
		#connection_04 = FullConnection(hidden_layer_03, hidden_layer_04)
		#connection_05 = FullConnection(hidden_layer_04, out_layer)
		#self.nn.addConnection(connection_01)
		#self.nn.addConnection(connection_02)
		#self.nn.addConnection(connection_03)
		#self.nn.addConnection(connection_04)
		#self.nn.addConnection(connection_05)
		#self.nn.sortModules()
		#self.nn.convertToFastNetwork()

	def buildInput(self, text):
		thought = self.lang.parse(text)
		data = [ 0 for i in range(len(self.lang)) ]
		for i in range(len(thought)):
			data[thought[i]] = 2 + (i / len(self.lang))
		#data = [ 1 if t in thought else -1 for t in range(len(self.lang)) ]
		return data

	def buildOutput(self, text):
		thought = self.thoughts.parse(text)
		data = [ 1 if t in thought else -1 \
				for t in range(len(self.thoughts)) ]
		return data

	def buildText(self, data):
		#for t in range(len(data)):
		#	if data[t] > 1.5:
		#		print("%i: %f" % (t, data[t]))
		#out = sorted([ t for t in range(len(data)) if data[t] > 1.5 ], key=functools.cmp_to_key(lambda x, y: data[x] - data[y]))
		out = [ t for t in range(len(data)) if data[t] > 0.75 ]
		#result = self.thoughts.synthesize(out) + " (%s)" \
		#		% ",".join([ "%1.2f" % data[t] for t in out ])
		result = self.thoughts.synthesize(out)
		return result

	def process(self, text):
		data = self.buildInput(text)
		result = self.nn.activate(data)
		return self.translate(self.buildText(result))

	def load(self, f):
		self.nn = pickle.load(f)
		self.nn.sorted = False
		self.nn.sortModules()

	def save(self, f):
		pickle.dump(self.nn, f)

	def multilearn(self, data):
		ds = SupervisedDataSet(len(self.lang), len(self.thoughts))
		for text in data:
			ds.addSample(self.buildInput(text),
					self.buildOutput(data[text]))
		#trainer = BackpropTrainer(self.nn, ds)
		trainer = BackpropTrainer(self.nn, ds, momentum=0.1,
				verbose=False, weightdecay=0.01)
		#return trainer.trainUntilConvergence()
		error = trainer.train()
		import sys
		#while error > self.error:
		for i in range(50):
			sys.stdout.write(".")
			sys.stdout.flush()
			error = trainer.train()
		return error

	def learn(self, text, answer):
		data = self.buildInput(text)
		result = self.buildOutput(answer)
		ds = SupervisedDataSet(len(data), len(result))
		ds.addSample(data, result)
		trainer = BackpropTrainer(self.nn, ds)
		error = trainer.train()
		#while error > self.error:
		#	error = trainer.train()
		return error

class Translate(object):
	def __init__(self, thoughts, messages):
		self.thoughts = thoughts
		self.messages = messages

	def translate(self, thought):
		if len(thought) == 0:
			return None
		t = set(self.thoughts.parse(thought))
		for name in self.messages:
			keys = self.thoughts.parse(name)
			common = list(t.intersection(keys))
			if (len(common) == len(t)) \
					and (len(common) == len(keys)):
				return self.messages[name]
		return None

	def __call__(self, thought):
		return self.translate(thought)

#class Translate(object):
#	def __init__(self, thoughts, lang, error=0.01):
#		self.error = error
#		self.thoughts = thoughts
#		self.lang = lang
#		thought_count = len(thoughts)
#		word_count = len(lang)
#		self.nn = buildNetwork(thought_count, 2 * max(word_count, thought_count), word_count, bias=True, hiddenclass=SigmoidLayer)
#		#in_layer = LinearLayer(words)
#		#hidden_layer_01 = SigmoidLayer(2 * words)
#		#hidden_layer_02 = SigmoidLayer(2 * words)
#		#hidden_layer_03 = SigmoidLayer(2 * words)
#		#out_layer = LinearLayer(words)
#		#self.nn = FeedForwardNetwork()
#		#self.nn.addInputModule(in_layer)
#		#self.nn.addModule(hidden_layer_01)
#		#self.nn.addModule(hidden_layer_02)
#		#self.nn.addModule(hidden_layer_03)
#		#self.nn.addOutputModule(out_layer)
#		#connection_01 = FullConnection(in_layer, hidden_layer_01)
#		#connection_02 = FullConnection(hidden_layer_01, hidden_layer_02)
#		#connection_03 = FullConnection(hidden_layer_02, hidden_layer_03)
#		#connection_04 = FullConnection(hidden_layer_03, out_layer)
#		#self.nn.addConnection(connection_01)
#		#self.nn.addConnection(connection_02)
#		#self.nn.addConnection(connection_03)
#		#self.nn.addConnection(connection_04)
#		#self.nn.sortModules()
#
#	def buildInput(self, text):
#		thought = self.lang.parse(text)
#		data = [ 1 if t in thought else -1 for t in range(len(self.lang)) ]
#		return data
#
#	def buildOutput(self, text):
#		thought = self.lang.parse(text)
#		data = [ 0 for i in range(len(self.lang)) ]
#		for i in range(len(thought)):
#			data[thought[i]] = 2 + i
#		#data = [ 1 if t in thought else -1 for t in range(len(self.lang)) ]
#		return data
#
#	def buildText(self, data):
#		#for t in range(len(data)):
#		#	if data[t] > 1.5:
#		#		print("%i: %f" % (t, data[t]))
#		out = sorted([ t for t in range(len(data)) if data[t] > 1 ], key=functools.cmp_to_key(lambda x, y: data[x] - data[y]))
#		#out = [ t for t in range(len(data)) if data[t] > 0.0 ]
#		result = self.lang.synthesize(out)
#		return result
#
#	def process(self, text):
#		data = self.buildInput(text)
#		result = self.nn.activate(data)
#		return self.buildText(result)
#
#	def load(self, f):
#		self.nn = pickle.load(f)
#		self.nn.sorted = False
#		self.nn.sortModules()
#
#	def save(self, f):
#		pickle.dump(self.nn, f)
#
#	def multilearn(self, data):
#		ds = SupervisedDataSet(len(self.lang), len(self.lang))
#		for text in data:
#			ds.addSample(self.buildInput(text), self.buildOutput(text))
#		trainer = BackpropTrainer(self.nn, ds)
#		error = trainer.train()
#		#while error > self.error:
#		for i in range(20):
#			error = trainer.train()
#		return error
