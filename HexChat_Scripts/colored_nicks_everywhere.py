import hexchat
import re

__module_name__ = "colored_nicks_everywhere"
__module_version__ = "0.6"
__module_description__ = "Colors nicks in messages with the same color X-Chat uses to display nicks"

# Load this script into X-Chat with: /py load <path_to>/colored_nicks_everywhere.py

normal_color = ""   # Adjust this if you display messages with a different color
#normal_color = "16"   # My config displays "Channel Message"s in bright-white

userList = []   # A cache of seen nicks (actually a queue of least-to-most-recent speakers).

# For stripping colors from a string
colorRe = re.compile(r"(||[0-9]{1,2}(,[0-9]{1,2}|))")
# For finding words in the message that could be a nick
nickRe = re.compile(r"[A-Za-z0-9_|/`'^\-\[\]\\]+")

def check_message(word, word_eol, event, userdata):
	nick_with_color = word[0]
	line_with_color = word[1]
	nick = colorRe.sub("",nick_with_color)
	line = colorRe.sub("",line_with_color)

	# Maintain userList
	if nick in userList:
		userList.remove(nick)
	if len(userList) > 200:
		del userList[0]
	userList.append(nick)

	# We do not do anything with lines which already contain color-codes.
	# This is important to avoid infinitely re-processing the message!  See below.
	if line != line_with_color:
		return hexchat.EAT_NONE

	# I was using hexchat.get_list("users") here to get an up-to-date userlist for
	# the channel, but it caused a memory leak!  (X-Chat 2.8.6-2.1)

	# Iterate through all nick-like words in the message
	# Build up newLine along the way
	iterator = nickRe.finditer(line)
	newLine = ""
	mode = ""
	reached = 0   # How much of the input string we have copied so far
	for match in iterator:
		word = match.group()
		# Check if the word is actually a user in the channel
		if word in userList:
			col = color_of(word)
			newWord = "" + str(col) + word + normal_color
			if event == "Your Message" or event == "Your Action":
				newLine = "\00330" + newLine + line[reached:match.span()[0]] + newWord + "\00330"
			else:
				newLine = newLine + line[reached:match.span()[0]] + newWord
			reached = match.span()[1]
	newLine = newLine + line[reached:len(line)]

	newLineWithoutColor = colorRe.sub("",newLine)
	if (newLineWithoutColor == newLine or newLine == line_with_color):
		# If we didn't adjust the line, then there is no need to re-emit it.
		return hexchat.EAT_NONE
	else:
		# Warning: This will get re-checked by check_message()!  But it should
		# reject it next time because now the line contains color codes.
		if event == "Channel Message":
			if mode_of(nick):
				hexchat.emit_print("Channel Message", nick, newLine, mode_of(nick))
				return hexchat.EAT_ALL
			else:
				hexchat.emit_print("Channel Message", nick, newLine)
				return hexchat.EAT_ALL
		
		elif event == "Channel Action":
			if mode_of(nick):
				hexchat.emit_print("Channel Action", nick, newLine, mode_of(nick))
				return hexchat.EAT_ALL
			else:
				hexchat.emit_print("Channel Action", nick, newLine)
				return hexchat.EAT_ALL
		
		elif event == "Your Message":
			if mode_of(nick):				
				hexchat.emit_print("Your Message", nick, newLine, mode_of(nick))
				return hexchat.EAT_ALL
			else:
				hexchat.emit_print("Your Message", nick, newLine)
				return hexchat.EAT_ALL
		
		elif event == "Your Action":
			if mode_of(nick):				
				hexchat.emit_print("Your Action", nick, newLine, mode_of(nick))
				return hexchat.EAT_ALL
			else:
				hexchat.emit_print("Your Action", nick, newLine)
				return hexchat.EAT_ALL
				
		elif event == "Private Message to Dialog":
			hexchat.emit_print("Private Message to Dialog", nick, newLine)
			return hexchat.EAT_ALL
			
		elif event == "Private Message":
			hexchat.emit_print("Private Message", nick, newLine)
			return hexchat.EAT_ALL
		
		elif event == "Private Action to Dialog":
			hexchat.emit_print("Private Action to Dialog", nick, newLine)
			return hexchat.EAT_ALL
			
		elif event == "Private Action":
			hexchat.emit_print("Private Action", nick, newLine)
			return hexchat.EAT_ALL
		

def mode_of(nick):
	for i in hexchat.get_list("users"):
		if nick == i.nick:
			return i.prefix

# A copy of the function from X-Chat:
rcolors = [ 19, 20, 22, 24, 25, 26, 27, 28, 29 ]
def color_of(nick):
	i=0
	sum=0
	while i<len(nick):
		c = nick[i]
		sum += ord(c)
		sum %= len(rcolors)
		i += 1
	return rcolors[sum]

# hexchat.hook_print("Channel Message", check_message)
hooks_filter = ["Channel Action", "Channel Message", "Your Message", "Your Action", "Private Message to Dialog", "Private Message", "Private Action to Dialog", "Private Action"]
for hook in hooks_filter:
    hexchat.hook_print_attrs(hook, check_message, hook, hexchat.PRI_HIGH)

print("Loaded "+__module_name__+" v"+__module_version__)

