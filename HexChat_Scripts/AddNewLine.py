# The MIT License (MIT)
# Copyright (c) <year> <copyright holders>
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from __future__ import print_function
from collections import deque
from sys import platform
import xchat as hexchat


__module_name__ = "New line"
__module_author__ = "Jevved"
__module_version__ = "1.0.0"
__module_description__ = "Adds a new line in the chat box"


if platform == 'darwin':
	primarymod = 1 << 28
else:
	primarymod = 1 << 2
shiftmod = 1 << 0


def get_valid_mod (mod):
	"""Modifiers are full of junk we dont care about, remove them"""
	return int(mod) & (1 << 0 | 1 << 2 | 1 << 3 | 1 << 28)


def keypress_cb(word, word_eol, userdata):

	key = word[0]
	mod = get_valid_mod(word[1])
	
	if (key, mod) == ('65293', primarymod):
		
		lasttext = hexchat.get_info('inputbox')
		newline = "\n"
		newtext	= lasttext + newline
		hexchat.command('settext {}'.format(newtext))
		hexchat.command('setcursor {}'.format(len(newtext)))


def unload_cb(userdata):
	print(__module_name__, 'version',  __module_version__, 'unloaded.')

hexchat.hook_print('Key Press', keypress_cb) 
hexchat.hook_unload(unload_cb)
print(__module_name__, 'version',  __module_version__, 'loaded.')
