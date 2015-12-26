# The MIT License (MIT)
# Copyright (c) 2016 - Dumm101
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

use strict;
use warnings;
use HexChat qw (:all);

my $NAME    = 'Newline';
my $VERSION = '1.0.0';
my $DESCRIPTION = 'Adds new line buffer when Ctrl+Enter pressed';
HexChat::register($NAME, $VERSION, $DESCRIPTION);

HexChat::print "$NAME Version $VERSION loaded\n";

hook_print('Key Press', \&check_keys);

sub callback {

	HexChat::print "$NAME unloaded\n"

}

sub check_keys {

	if ($_[0][0] == 65293 && $_[0][1] & 4) {
		
		my $lasttext = HexChat::get_info 'inputbox';
		my $newline = "\n";
		my $newtext = $lasttext.$newline;
		
		HexChat::command "settext $newtext";
		HexChat::command 'setcursor ' . length $newtext;
		
	}
	
	else {
		return EAT_NONE;
	}
}