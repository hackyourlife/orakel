# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from random import randrange as random

def oneof(values):
	return values[random(len(values))]
