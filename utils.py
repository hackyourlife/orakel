# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from random import randrange as random

def oneof(values):
	return values[random(len(values))]

def startswith(a, b):
	if len(b) > len(a):
		return False
	if len(b) == 0:
		return True
	for i in range(len(b)):
		if a[i] != b[i]:
			return False
	return True
