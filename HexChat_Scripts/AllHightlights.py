import hexchat
import re

__module_name__ = "AllHighlights"
__module_version__ = "0.1"
__module_description__ = "Highlight me for any nicks in channel"
__module_author__ = "Dummy101"

colorRe = re.compile(r"(||[0-9]{1,2}(,[0-9]{1,2}|))")
_recursion = False

def check_if_nick(word, word_to_eol, event, userdata):
	global _recursion
	if _recursion:
		return
	
	words_raw = set([re.sub(r'[^\w]', '', i) for i in word[1].lower().split()])
	chan_users = hexchat.get_list('users')
	
	chan_users_stripped = [re.sub(r'[^\w]', '', colorRe.sub("", i.nick.lower())) for i in chan_users]

	for i in words_raw:
		if i in chan_users_stripped:
			nickc = nickc = colorRe.sub("", word[0])
			if len(word) == 2:
				word.append('')
			_recursion = True
			if event == "Channel Message":
				hexchat.emit_print("Channel Msg Hilight", '\x0319'+nickc, '\x0319'+word[1], '\x0319'+word[2])
				hexchat.command("gui flash")
			elif event == "Channel Action":
				hexchat.emit_print("Channel Action Hilight", '\x0319'+nickc, '\x0319'+word[1], '\x0319'+word[2])
				hexchat.command("gui flash")
			_recursion = False
			
			return hexchat.EAT_ALL

hooks_filter = ["Channel Message", "Channel Action"]
for hook in hooks_filter:
    hexchat.hook_print_attrs(hook, check_if_nick, hook, hexchat.PRI_HIGH)

def unload_cb(userdata):
	hexchat.prnt(__module_name__ +' version '+ __module_version__+' unloaded.')

hexchat.hook_unload(unload_cb)
hexchat.prnt(__module_name__ +' version '+ __module_version__+' loaded.')