#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Revision: 1.7 $
# 
# Copyright (c) 2015-2016 William S. Annis
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

import codecs
import re
import sys
from wordgen import textify


class UnknownOption(Exception): pass

class ParseError(Exception): pass


class PhonologyDefinition(object):
    def __init__(self, soundsys, fname):
        """Expects a SoundSystem instance for the first argument."""
        self.soundsys = soundsys
        self.fname = fname
        self.options = []
        self.features = []
        self.macros = {}
        # For sanity checking at the end
        self.letters = []
        self.ph_classes = []   # phoneme classes
        self.parse()
        self.sanity_check()

    def parse(self):
        with codecs.open(self.fname, encoding='utf-8') as f:
            # The loop over the file is handled this way to let me
            # pass in the file handle to a subparser.
            line = f.readline()
            while line != '':
                line = re.sub(r'#.*', '', line)   # comments
                line = line.strip()
                if line == '': 
                    line = f.readline()
                    continue
                if re.match(ur'with:', line):
                    self.parse_option(line[5:].strip())
                elif re.match(ur'random-rate:', line):
                    self.parse_random_rate(line[12:].strip())
                elif re.match(ur'filter:', line):
                    self.parse_filter(line[7:].strip())
                elif re.match(ur'reject:', line):
                    self.parse_reject(line[7:].strip())
                elif re.match(ur'words:', line):
                    self.parse_words(line[6:].strip())
                elif re.match(ur'letters:', line):
                    self.parse_letters(line[8:].strip())
                elif line[0] == '%':
                    self.parse_clusterfield(line, f)
                elif '=' in line:
                    self.parse_class(line)
                else:
                    raise ParseError, line
                line = f.readline()
        # A non-fatal bit of sanity checking and warning.
        if (self.soundsys.use_assim or self.soundsys.use_coronal_metathesis) and self.soundsys.sorter is None:
            sys.stderr.write("Without 'letters:' cannot apply assimilations or coronal metathesis.\n\n")

# add option to remove: ji, wu, bw, dl, etc. forbid onset
# clusters from the same place 
    def parse_option(self, line):
        for option in line.split():
            if option == 'std-ipa-features':
                #print "Loaded IPA..."
                self.soundsys.use_ipa()
            elif option == 'std-digraph-features':
                self.soundsys.use_digraphs()
            elif option == 'std-assimilations':
                #print "Loaded assimilations..."
                self.soundsys.with_std_assimilations()
            elif option == 'coronal-metathesis':
                self.soundsys.with_coronal_metathesis()
            else:
                raise UnknownOption, option    

    def add_filter(self, pre, post):
        pre = pre.strip()
        #pre = pre.replace("\\", "\\\\")
        post = post.strip()
        #post = post.replace("\\", "\\\\")
        self.soundsys.add_filter(pre, post)
        
    def parse_filter(self, line):
        for filt in line.split(";"):
            # First, check for a redundant semicolon at the end of the
            # line, resulting in a blank entry.
            filt = filt.strip()
            if filt == '': continue

            # Now we can parse the filter.
            (pre, post) = filt.split(">")
            self.add_filter(pre, post)

    def parse_reject(self, line):
        for filt in line.split():
            self.soundsys.add_filter(filt, 'REJECT')

    def parse_letters(self, line):
        self.letters = line.split()
        self.soundsys.add_sort_order(line)

    def parse_words(self, line):
        line = self.expand_macros(line)
        for (n, word) in enumerate(line.split()):
            # Crude Zipf distribution for word selection.
            self.soundsys.add_rule(word, 10.0 / ((n + 1) ** .9))

    def expand_macros(self, word):
        for (macro, value) in self.macros.items():
            word = re.sub(macro, value, word)
        return word

    def parse_class(self, line):
        (sclass, values) = line.split("=")
        sclass = sclass.strip()
        values = values.strip()
        if sclass[0] == u'$':
            self.macros["\\" + sclass] = values
        else:
            self.ph_classes += values.split()
            self.soundsys.add_ph_unit(sclass, values)

    def parse_clusterfield(self, line, fh):
        c2list = line.split()[1:]  # ignore leading %
        # Width of all rows must be 'n'.
        n = len(c2list)
        line = fh.readline()
        while line not in ('', '\n'):
            # filter comments
            line = re.sub(r'#.*', '', line)   # comments
            line = line.strip()
            if line == '':
                line = fh.readline()
                continue
            row = line.split()
            c1 = row[0]
            row = row[1:]
            if len(row) == n:
                for (i, result) in enumerate(row):
                    if result == '+':
                        continue
                    if result == '-':
                        self.soundsys.add_filter(c1 + c2list[i], 'REJECT')
                    else:
                        self.add_filter(c1 + c2list[i], result)
            elif len(row) > n:
                raise ParseError, "Cluster field row too long: " + line
            else:
                raise ParseError, "Cluster field row too short: " + line
            line = fh.readline()

    def parse_random_rate(self, line):
        self.soundsys.randpercent = int(line)

    def sanity_check(self):
        # Can't do sanity checking if the letters: directive isn't used.
        if len(self.letters) == 0: return
        letters = set(self.letters)
        phonemes = set(self.ph_classes)
        if not phonemes <= letters:
            diff = list(phonemes - letters)
            msg = u"** A phoneme class contains '{}' missing from 'letters'.\n".format(" ".join(diff))
            sys.stderr.write(msg.encode('utf-8'))
            sys.stderr.write("** Strange word shapes are likely to result.\n")

    def generate(self, n=1, unsorted=False):
        return self.soundsys.generate(n, unsorted)

    def paragraph(self, sentences):
        return textify(self.soundsys, sentences)
    

if __name__ == '__main__':
    from wordgen import SoundSystem, textify
    
    pd = PhonologyDefinition(SoundSystem(), "t.def")
    #print(textify(pd.soundsys, 25).encode('utf-8'))
    print(pd.paragraph(15).encode('utf-8'))
    #print(pd.generate(50))
