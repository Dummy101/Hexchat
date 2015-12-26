"""
LICENSE AGREEMENT:
 
Copyright (c) 2005, psichron.za.net
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
    * Neither the name of Carel van Wyk nor the names of his contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Version History:
    1.0 beta released 06 January 2007
    10 january: revision2: bugfix #2 : save config file to dcc_dir directory from xchat /set
    13 January: revision3: error on invalid number of parameters
    20 January: revision4: added \ to path. sorry!
    4 Feb: xaop.ini 's location changed. Now saves to user's home directory as .xaop
"""

# Please report any errors or submit any requests at http://xaop.psichron.za.net
# OR email xaop[at]psichron.za.net
# Eitan Adler <lists@eitanadler.com>
#TODO:

# See http://labix.org/xchat-python for details on xchat python scripting

__module_name__ = "pyXAOP" 
__module_version__ = "beta 1.0 revision 5" 
__module_description__ = "Xchat Auto-op Script by psi, type /xaop help" 
 
import xchat
import re
import pickle
import os
import hexchat
from pickle import *
 
CHANNEL_PREFIXES = ['#','&','!']
CHANNEL_ALL_MASK = "ALL"
NETWORK_ALL_MASK = "ALL"
OPERATOR_PREFIXES = ['~', '&', '@']     # Halfop (%) not supported
IRC_HOSTMASK_REGEX = r'^([a-zA-Z0-9\[\]\\^_-{|}*]+)!([a-zA-Z0-9\[\]\\^_-{|}~*]+)@([a-zA-Z0-9*.-]+)$'
HOSTNAME_REGEX = r'^[a-zA-Z0-9.-]+$'
# !!! "\" HAS to be the first character to be escaped. Bug Fix 1
REGEX_META_CHARS = r'\ . ^ { [ ] | }'   # Note: this is not a full list.
# CONFIG_FILE_LOCATION = hexchat.get_info('configdir')+"/xaop.txt" # Location of config file (Changed for revision 5)
# CONFIG_FILE_LOCATION = os.path.join(hexchat.get_info("configdir"), "xaop.txt")
CONFIG_DIR_LOCATION = hexchat.get_info("configdir")
CONFIG_FILE_LOCATION = CONFIG_DIR_LOCATION + "\\addons\\xaop.txt"

def isOperator():
    """Return True if you are an operator in the channel of the current context,
    False if not."""
    myNick = xchat.get_info("nick")
    userlist = xchat.get_list("users") 
    userPrefixes = dict([(user.nick,user.prefix) for user in userlist])
    return (userPrefixes[myNick] in OPERATOR_PREFIXES)
        
def nickMatchesMask(nick,mask):
    """Match a nick (nick!ident@host) against an "/xaop add" supplied mask.
    Returns True of matched."""
    for ch in REGEX_META_CHARS.split(' '): # First escape regex metacharacters
        mask = mask.replace(ch, "\\"+ch)
    mask = mask.replace("*",".*")
    p = re.compile(mask,re.IGNORECASE)
    return p.match(nick) != None
    

#word[0] is the nick
#word[1] is the channel joined
#word[2] is ident@host
def processJoin(word, word_eol,userdata):
    """Process a Join event.OP user if found in xaop list"""
    if not isOperator():
            return xchat.EAT_NONE
    # else:    

    for line in aopList:
        if (word[1].lower() in line["channels"].lower().split(',')) \
        or (line["channels"].upper() == CHANNEL_ALL_MASK): # Check that current channel is in channel list
            if (xchat.get_info("network").lower() in line["networks"].lower().split(',')) \
            or (line["networks"].upper() == NETWORK_ALL_MASK): # Check that current network is in network list
                if nickMatchesMask(word[0]+"!"+word[2], line["hostmask"]): # Check that nick matches mask
                    xchat.command("op %s" % (word[0]))
                    break

    return xchat.EAT_NONE


def isValidMask(mask):
    """Returns True if "/xaop add" supplied "mask" is a valid hostmask"""
    p = re.compile(IRC_HOSTMASK_REGEX)
    return p.match(mask) != None
    
def isValidChannelList(channelList):
    """Returns True if "/xaop add" supplied channel list is valid"""
    if channelList.upper() == CHANNEL_ALL_MASK:
        return True
    for channel in channelList.split(','):
        if not channel[0] in CHANNEL_PREFIXES:
            return False
    # else:
    return True

def isValidNetworkList(networkList):
    """Returns True if "/xaop add" supplied network list is valid"""
    if networkList.upper() == NETWORK_ALL_MASK:
        return True
    p = re.compile(HOSTNAME_REGEX,re.IGNORECASE)
    for network in networkList.split(','):
        if p.match(network) == None:
            return False
    # else:
    return True

# params[0] should be an integer
def removeAop(params):
    """Process /xaop remove <list number>. Removes item from list and saves"""
    # Check that there is a parameter[0], that it is a number, and that it is within range in aopList
    try:
        if len(params) != 1:
            print ("Invalid number of parameters")
            raise IndexError("Print this noob some help")
        if params[0].isdigit():
            if not (int(params[0])-1) in range(len(aopList)): 
                raise IndexError("Print this noob some help")
    except IndexError:
        printHelp()
        return

    # Remove element at index and save
    removed = aopList.pop(int(params[0])-1)
    print ("  ".join(["Removed ",removed["hostmask"],removed["channels"],removed["networks"]]))
    printList()
    
    f = open(CONFIG_FILE_LOCATION,"wb") 
    pickle.dump(aopList,f)
    f.close()

# params[0] should be the hostmask in the form nick!ident@host
# params[1] should be the channel or channel list, seperated by "," , or CHANNEL_ALL_MASK
# params[2] should be the network or network lsit, seperated by "," , or NETWORK_ALL_MASK
# If params[1] is omitted, NETWORK_ALL_MASK and CHANNEL_ALL_MASK is assumed
# If params[2] is omitted, NETWORK_ALL_MASK is assumed
def addAop(params):
    """Process /xaop add nick!ident@host #ch1,#ch2 net1,net2... Adds item to
    list and saves"""
    if len(params) == 1:
        params.insert(1,CHANNEL_ALL_MASK)
    if len(params) == 2:
        params.insert(2,NETWORK_ALL_MASK)
    # Checks that we have at least three parameters, and that they are valid
    try:
        if len(params) >= 4:
            print ("Too many parameters!")
            raise IndexError("Print this noob some help")
        if  not isValidMask(params[0]) \
        or not isValidChannelList(params[1]) \
        or not isValidNetworkList(params[2]):
            print ("INVALID ADD STRING!\n")
            raise IndexError("Print this noob some help")
    except IndexError:
        printHelp()
        return
    #else:
    aopList.append( {"hostmask": params[0], "channels": params[1], "networks": params[2]} )
    print ("  ".join(["Added",params[0],params[1],params[2]]))
    printList()
    # ctable = aopList
    f = open(CONFIG_FILE_LOCATION,"wb")
    pickle.dump(aopList,f)
    f.close()

def printList():
    """Outputs the current aop list to screen."""
    counter = 1
    for line in aopList:
        print ("\t%d: %s\t%s\t%s" % (counter,line["hostmask"],line["channels"],line["networks"]))
        counter += 1 

def printHelp():
    """Outputs help to screen."""
    print ("=== XChat Auto-Op script by psi. Version "+__module_version__+" ===")
    print ("  Please report any errors or submit requests to http://xaop.psichron.za.net\n")
    print ("ADD A HOSTMASK WITH SPECIFIED CHANNELS AND NETWORKS TO AOP LIST:")
    print ("  /xaop add nick!ident@host #ch1,#ch2,#ch3 network1,network2")
    print ("ADD A HOSTMASK FOR ALL USERS ON ALL CHANNELS AND ALL NETWORKS:")
    print ("  /xaop add *!*@* ALL ALL")
    print ("PRINT THE AOP LIST:")
    print ("  /xaop list")
    print ("REMOVE AN ITEM FROM THE AOP LIST:")
    print ("  /xaop remove <number from /xaop list>")
    print ("EXAMPLE:  /xaop add psi*!*@*.za.net #programming,#python shadowfire")
    

def xaop_callback(word, word_eol, userdata):
    # """Called by hooked command /xaop."""
    try:
        if word[1].lower() == "add": 
            addAop(word[2:])
        elif word[1].lower() == "remove":
            removeAop(word[2:])
        elif word[1].lower() == "list":
            printList()
        else:
            printHelp()
    except IndexError:
        printHelp()
    
    return xchat.EAT_ALL

xchat.hook_print("Join",processJoin)
xchat.hook_command("xaop", xaop_callback, help="/xaop add|remove|list|help") 

# Load the aop list from a file:

try:
    f = open(CONFIG_FILE_LOCATION,"rb")
    aopList = pickle.load(f)
    f.close()
except IOError:
    aopList = []
except EOFError:
    aopList = []

def unload_cb(userdata):
    hexchat.prnt(__module_name__ + ' version ' + __module_version__+ ' unloaded.')

hexchat.hook_unload(unload_cb)
hexchat.prnt(__module_name__ + ' version ' + __module_version__+ ' loaded.')