# -*- coding: utf-8 -*-

#        DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
#                    Version 2, December 2004 
#
# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net> 
#
# Everyone is permitted to copy and distribute verbatim or modified 
# copies of this license document, and changing it is allowed as long 
# as the name is changed. 
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION 
#
#  0. You just DO WHAT THE FUCK YOU WANT TO.

import vista

class Context(object):
	def think(self, dt, events, keys, mousepos, buttons):
		pass
		
	def draw(self):
		vista.clear()


cstack = []

def push(con):
	cstack.append(con)

def pop(n = 1):
	for _ in range(n):
		if cstack:
			del cstack[-1]

def top():
	return cstack[-1] if cstack else None