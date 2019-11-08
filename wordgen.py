#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# $Revision: 1.4 $
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


from distribution import WeightedSelector
import random
import re
import math
import SmartClusters as sc
import codecs
import textwrap
import sys


class RuleError(Exception): pass


# Define an arbitrary sort order, in unicode and possibly including
# di- or n-graphs.  It ain't efficient, but it works.
class ArbSorter:
    def __init__(self, order):
        self.graphs = re.split('\s*', order, flags=re.UNICODE)
        # Create a regex to split on each character or multicharacter
        # sort key.  (As in "ch" after all "c"s, for example.)
        split_order = sorted(self.graphs, key=len, reverse=True)
        split_order.append(".")
        self.splitter = re.compile("(%s)" % "|".join(split_order), re.UNICODE)
        # Next, collect ints for the ordering and the lookup
        # for putting words back together.
        self.ords = {}
        self.vals = []
        for i in range(len(self.graphs)):
            self.ords[self.graphs[i]] = i
            self.vals.append(self.graphs[i])

    # Turns a word into a list of ints representing the new
    # lexicographic ordering.  Python, helpfully, allows one to
    # sort ordered collections of all types, including lists.
    def word_as_values(self, word):
        w = self.splitter.split(word)[1::2]
        try:
            arrayed_word = [self.ords[char] for char in w]
        except KeyError:
            msg = "Word with unknown letter: '%s'." % word
            utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)
            print(msg, file=utf8stdout)
            print("A filter or assimilation might have caused this.")
            sys.exit(1)
        return arrayed_word

    def values_as_word(self, values):
        return "".join([self.vals[v] for v in values])

    def split(self, word):
        return self.splitter.split(word)[1::2]

    def __call__(self, l):
        l2 = [self.word_as_values(item) for item in l]
        l2.sort()
        return [self.values_as_word(item) for item in l2]


# Weighted random selection.
def select(dic):
    total = sum(dic.values())
    pick = random.uniform(0, total-1)
    tmp = 0
    for key, weight in dic.items():
        tmp += weight
        if pick < tmp:
            return key

# Give approximately natural frequencies to phonemes.
# Gusein-Zade law.
def jitter(v, percent=10.0):
    move = v * (percent / 100.0)
    return v + (random.random() * move) - (move / 2)

# Takes a whitespace delimited string, returns a string
# in the form expected by SoundSystem.add_ph_unit().
def natural_weights(phonemes):
    p = phonemes.split()
    n = len(p)
    weighted = {}
    for i in range(n):
        weighted[p[i]] = jitter((math.log(n + 1) - math.log(i + 1)) / n * 100)
    return ' '.join(['%s:%.2f' % (p, v) for (p, v) in list(weighted.items())])

def rule2dict(rule):
    items = rule.split()
    d = {}
    for item in items:
        if ':' not in item:
            raise RuleError('%s not a valid phoneme and weight' % item)
        (value, weight) = item.split(':')
        d[value] = float(weight)
    return d


class SoundSystem:
    def __init__(self):
        self.phonemeset = {}
        self.ruleset = {}
        self.filters = []
        self.randpercent = 10
        self.use_assim = False
        self.use_coronal_metathesis = False
        self.sorter = None

    def add_ph_unit(self, name, selection):
        # add natural weights if there's no weighting.
        if ':' not in selection:
            selection = natural_weights(selection)
            #print('%s = %s' % (name, selection))
        self.phonemeset[name] = WeightedSelector(rule2dict(selection))

    def add_rule(self, rule, weight):
        # add rule verification
        self.ruleset[rule] = weight

    # rules allow phonemes to be in the rule, too: CyVN
    def run_rule(self, rule):
        """Generate a single instance of a rule run."""
        n = len(rule)
        s = []
        for i in range(n):
            # Skip control characters.
            if rule[i] in ['?', '!']: continue
            # Sound that occurs optionally at random.
            if i<(n-1) and rule[i+1] == '?':
                if random.randint(0, 100) < self.randpercent:
                    if rule[i] in self.phonemeset: # phoneme class
                        s.append(self.phonemeset[rule[i]].select())
                    else: # literal
                        s.append(rule[i])
            # Sound that must not duplicate the previous sound.
            elif i<(n-1) and i > 0 and rule[i+1] == "!":
                # First, if the previous class was optional, we need
                # to skip back one more to check against the class
                # rather than the '?'.
                if rule[i-1] == '?' and i - 2 >= 0:
                    prevc = rule[i-2]
                else:
                    prevc = rule[i-1]
                    #                if (rule[i] != rule[i-1]):
                # Make sure this is even a duplicate environment.
                if (rule[i] != prevc):
                    raise RuleError("Misplaced '!' option: in non-duplicate environment: {}.".format(rule))
                if rule[i] in self.phonemeset:
                    nph = self.phonemeset[rule[i]].select()
                    while nph == s[-1]:
                        nph = self.phonemeset[rule[i]].select()
                    s.append(nph)
                else:
                    raise RuleError("Use of '!' here makes no sense: {}".format(rule))
            # Just a normal sound.
            elif rule[i] in self.phonemeset:
                s.append(self.phonemeset[rule[i]].select())
            else: # literal
                s.append(rule[i])
        return "".join(s)

    def add_filter(self, pat, repl):
        if repl == '!':
            self.filters.append((pat, ""))
        else:
            self.filters.append((pat, repl))    

    def apply_filters(self, word):
        # First, if assimilations and metathesis are in play, apply those.
        if self.sorter:
            w = self.sorter.split(word)
            if self.use_assim:
                w = sc.apply_assimilations(w)
            if self.use_coronal_metathesis:
                w = sc.apply_coronal_metathesis(w)
            word = "".join(w)

        # Now the filters.
        for (pat, repl) in self.filters:
            word = re.sub(pat, repl, word)
            if re.search('REJECT', word, flags=re.UNICODE):
                return 'REJECT'
        return word

    def add_sort_order(self, order):
        self.sorter = ArbSorter(order)

    def use_ipa(self):
        sc.initialize()

    def use_digraphs(self):
        sc.initialize('digraph')

    def with_std_assimilations(self):
        self.use_assim = True

    def with_coronal_metathesis(self):
        self.use_coronal_metathesis = True

    def generate(self, n=10, unsorted=False):
        """Generate n unique words randomly from the rules."""
        words = set()
        while len(words) < n:
            rule = select(self.ruleset)
            word = self.apply_filters(self.run_rule(rule))
            if word != 'REJECT':
                words.add(word)
        words = list(words)
        if not unsorted:
            if self.sorter is not None:
                words = self.sorter(words)
            else:
                words.sort()
        return words


def textify(phsys, sentences=11):
    """Generate a fake paragraph of text from a sound system."""
    text = ""
    for i in range(sentences):
        sent = random.randint(3, 11)
        if sent >= 7:
            comma = random.randint(0, sent - 2)
        else:
            comma = -1
        text += phsys.generate(1, unsorted=True)[0].capitalize()
        for j in range(sent):
            text += " " + phsys.generate(1, unsorted=True)[0]
            if j == comma:
                text += ","
        if random.randint(0, 70) <= 70:
            text += ". "
        else:
            text += "? "
    text = textwrap.wrap(text, 70)
    return "\n".join(text)


if __name__ == '__main__':
    m1 = SoundSystem()
    m1.add_ph_unit('V', 'a i á u o')
    m1.add_ph_unit('C', 't n k l h ch m s ɬ p š')
    m1.add_ph_unit('F', 'n l s')
    m1.add_sort_order('a á ch h i k l ɬ m n o p s š t u y')
    m1.add_filter(r'hy', r'š')
    m1.add_filter(r'(lł|lł)', r'l')
    m1.add_filter(r's(t|k)', r'\1s')
    m1.add_filter(r'nn|ll|ss|sš', 'REJECT')
    m1.add_rule('V?Cy?VF?', 5)
    m1.add_rule('V?CVF?CV', 7)

#print(m1.phonemeset)
#print(m1.run_rule('CVC?'))
#n = console.input_alert('wordgen', 'How many words?', '100')
    n = 50
    utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)
    print(' '.join(m1.generate(int(n))), file=utf8stdout)
    print()
    print(textify(m1), file=utf8stdout)
#print(m1.apply_filters('alła'))
#print(m1.apply_filters('isti'))
#print(m1.apply_filters('lassa'))
