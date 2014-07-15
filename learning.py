#!/bin/python
# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import neuronal.language
import neuronal.brain

import logging

log = logging.getLogger(__name__)

def load_messages(filename):
	messages = {}
	with open("answers.lima") as f:
		for line in f:
			line = line.strip()
			if len(line) == 0:
				continue
			if line[0] == '#':
				continue
			tokens = line.split(";")
			thought = tokens[0].strip()
			text = tokens[1].strip()
			messages[thought] = text
	return messages

class Learning(object):
	def __init__(self, word_file, synonym_file, thought_file, message_file,
			brain_file):
		lang = neuronal.language.Language()
		lang.load(word_file)
		lang.load_synonyms(synonym_file)
		thoughts = neuronal.language.Language()
		thoughts.load(thought_file)
		messages = load_messages(message_file)
		log.info("%d words, %d thoughts, %d messages" \
				% (len(lang), len(thoughts), len(messages)))

		self.brain = neuronal.brain.Brain(lang, thoughts, messages)
		with open(brain_file, "rb") as f:
			self.brain.load(f)

	def answer(self, question):
		try:
			return self.brain.process(question)
		except Exception as e:
			log.warn(e)
			return None

	def __call__(self, message, nick, send_message):
		result = self.answer(message.strip())
		if not result is None:
			send_message(result)
			return True
		return False

if __name__ == "__main__":
	dataset = {}
	with open("training.lima") as f:
		for line in f:
			line = line.strip()
			if len(line) == 0:
				continue
			if line[0] == '#':
				continue
			tokens = line.split(";")
			thought = tokens[0].strip()
			text = tokens[1].strip()
			dataset[text] = thought

	lang = neuronal.language.Language()
	lang.load("words.lima")
	lang.load_synonyms("synonyms.lima")
	thoughts = neuronal.language.Language()
	thoughts.load("thoughts.lima")
	messages = load_messages("answers.lima")
	log.info("%d words, %d thoughts, %d messages" \
			% (len(lang), len(thoughts), len(messages)))

	brain = neuronal.brain.Brain(lang, thoughts, messages)
	print(brain.multilearn(dataset))
	with open("brain.state", "wb") as f:
		brain.save(f)

	def do(x):
		print("%s -> %s" % (x, brain.process(x)))

	for x in [
			"wie kann ich ein Ticket erstellen?",
			"wo kann ich ein Ticket anlegen?",
			"jemand da?",
			"hallo jemand da?",
			"hallo, ist jemand da?",
			"ist da jemand?",
			"niemand da?",
			"ist der burgi hier?",
			"kann man hier eine hompage auch machen",
			"kann man hier eine webseite machen",
			"penis"]:
		do(x)

	for x in dataset:
		do(x)
