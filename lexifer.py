#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Revision: 1.2 $
# 
# Copyright (c) 2015 William S. Annis
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""William's Crazy Word Generator
"""

import argparse
import textwrap
from sys import stderr
from PhDefParser import PhonologyDefinition
from wordgen import SoundSystem, textify


# Deal with arguments.
opt = argparse.ArgumentParser()
opt.add_argument("file", help="phonology definition file")
opt.add_argument("-n", "--number", help="how many words to generate", type=int)
opt.add_argument("-u", "--unsorted", help="print out words unsorted",
                 action="store_true")
opt.add_argument("-o", "--one-per-line", help="print one word per line",
                 action="store_true")
args = opt.parse_args()

# And off we go!  Parse the definition file.
pd = PhonologyDefinition(SoundSystem(), args.file)

# Generate some words...
if args.number is None:
    # Default behavior - print out a paragraph of text.
    if args.unsorted:
        stderr.write("** 'Unsorted' option ignored in paragraph mode.\n\n")
    if args.one_per_line:
        stderr.write("** 'One per line' option ignored in paragraph mode.\n\n")
    print textify(pd.soundsys, 25).encode('utf-8')
else:
    # Just a wordlist.
    words = pd.generate(args.number, args.unsorted)
    if args.one_per_line:
        for w in words:
            print(w.encode('utf-8'))
    else:
        words = textwrap.wrap(" ".join(words), 70)
        print("\n".join(words).encode('utf-8'))
    

# EOF
