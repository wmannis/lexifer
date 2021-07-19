#!/usr/bin/env python   # -*- coding: utf-8 -*-
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

"""
Perform certain kinds of word fixing from basic phonological
knowledge, stored in the form of a SQL database, which I abuse
horribly to get the answers I want.
"""

import sqlite3 as sql
global phdb


DATA = [# Bilabial, labio-dental
  ('p', 'p', 'voiceless', 'bilabial', 'stop'),
  ('b', 'b', 'voiced', 'bilabial', 'stop'),
  ('ɸ', 'ph', 'voiceless', 'bilabial', 'fricative'),
  ('β', 'bh', 'voiced', 'bilabial', 'fricative'),
  ('f', 'f', 'voiceless', 'labiodental', 'fricative'),
  ('v', 'v', 'voiced', 'labiodental', 'fricative'),
  ('m', 'm', 'voiced', 'bilabial', 'nasal'),
  ('m', 'm', 'voiced', 'labiodental', 'nasal'),
  # Alveolar
  ('t', 't', 'voiceless', 'alveolar', 'stop'),
  ('d', 'd', 'voiced', 'alveolar', 'stop'),
  ('s', 's', 'voiceless', 'alveolar', 'sibilant'),
  ('z', 'z', 'voiced', 'alveolar', 'sibilant'),
  ('θ', 'th', 'voiceless', 'alveolar', 'fricative'),
  ('ð', 'dh', 'voiced', 'alveolar', 'fricative'),
  ('ɬ', 'lh', 'voiceless', 'alveolar', 'lateral fricative'),
  ('ɮ', 'ldh', 'voiced', 'alveolar', 'lateral fricative'),
  ('tɬ', 'tl', 'voiceless', 'alveolar', 'lateral affricate'),
  ('dɮ', 'dl', 'voiced', 'alveolar', 'lateral affricate'),
  ('ts', 'ts', 'voiceless', 'alveolar', 'affricate'),
  ('dz', 'dz', 'voiced', 'alveolar', 'affricate'),
  ('ʃ', 'sh', 'voiceless', 'postalveolar', 'sibilant'),
  ('ʒ', 'zh', 'voiced', 'postalveolar', 'sibilant'),
  ('tʃ', 'ch', 'voiceless', 'postalveolar', 'affricate'),
  ('dʒ', 'j', 'voiced', 'postalveolar', 'affricate'),
  ('n', 'n', 'voiced', 'alveolar', 'nasal'),
  # Retroflex
  ('ʈ', 'rt', 'voiceless', 'retroflex', 'stop'),
  ('ɖ', 'rd', 'voiced', 'retroflex', 'stop'),
  ('ʂ', 'sr', 'voiceless', 'retroflex', 'sibilant'),
  ('ʐ', 'zr', 'voiced', 'retroflex', 'sibilant'),
  ('ʈʂ', 'rts', 'voiceless', 'retroflex', 'affricate'),
  ('ɖʐ', 'rdz', 'voiced', 'retroflex', 'affricate'),
  ('ɳ', 'rn', 'voiced', 'retroflex', 'nasal'),
  # Velar
  ('k', 'k', 'voiceless', 'velar', 'stop'),
  ('g', 'g', 'voiced', 'velar', 'stop'),
  ('x', 'kh', 'voiceless', 'velar', 'fricative'),
  ('ɣ', 'gh', 'voiced', 'velar', 'fricative'),
  ('ŋ', 'ng', 'voiced', 'velar', 'nasal'),
  # Uvular
  ('q', 'q', 'voiceless', 'uvular', 'stop'),
  ('ɢ', 'gq', 'voiced', 'uvular', 'stop'),
  ('χ', 'qh', 'voiceless', 'uvular', 'fricative'),
  ('ʁ', 'gqh', 'voiced', 'uvular', 'fricative'),
  ('ɴ', 'nq', 'voiced', 'uvular', 'nasal')]


def initialize(notation="ipa"):
    global phdb
    phdb = sql.connect(':memory:')
    c = phdb.cursor()
    c.execute("""create table phdb
                (phoneme text, voice text, place text, manner text)""")
    if notation == 'ipa':
        for (ph, ignore, v, p, m) in DATA:
            c.execute("insert into phdb values (?,?,?,?)", (ph, v, p, m))
    elif notation == 'digraph':
        for (ignore, ph, v, p, m) in DATA:
            c.execute("insert into phdb values (?,?,?,?)", (ph, v, p, m))
    else:
        raise Error("Unknown notation: %s" % notation)
    phdb.commit()

def nasal_assimilate(ph1, ph2):
    c = phdb.cursor()
    m = c.execute("""select phoneme from phdb 
        where (select manner from phdb where phoneme = ?) = 'nasal'
        and manner = 'nasal'
        and place = (select place from phdb where phoneme = ?)""", (ph1, ph2))
    m = m.fetchall()
    if len(m) == 0:
        return ph1
    else:
        return m[0][0]

def voice_assimilate(ph1, ph2):
    c = phdb.cursor()
    m = c.execute("""select phoneme from phdb
        where place = (select place from phdb where phoneme = ?)
        and manner = (select manner from phdb where phoneme = ?)
        and (select manner from phdb where phoneme = ?) != 'nasal'
        and voice = (select voice from phdb where phoneme = ?)
    """, (ph1, ph1, ph2, ph2))
    m = m.fetchall()
    if len(m) == 0:
        return ph1
    else:
        return m[0][0]
    
def coronal_metathesis(ph1, ph2):
    c = phdb.cursor()
    m1 = c.execute("select phoneme from phdb where phoneme = ? and place = 'alveolar'", (ph1,))
    m1 = m1.fetchall()
    if len(m1) == 0:
        return ph1, ph2
    m2 = c.execute("""select phoneme from phdb
        where phoneme = ? 
        and place in ('velar', 'bilabial')
        and manner in ('stop', 'nasal')
        and (select manner from phdb where phoneme = ?) = (select manner from phdb where phoneme = ?)""", (ph2, ph2, ph1))
    m2 = m2.fetchall()
    if len(m2) == 0:
        return ph1, ph2
    else:
        return ph2, ph1


# The "apply_" functions expect a word that has been split into
# an array of phonemes.
def apply_assimilations(word):
    new = word[:]
    for i in range(len(word) - 1):
        new[i] = voice_assimilate(word[i], word[i+1])
        new[i] = nasal_assimilate(new[i], word[i+1])
    return new
#
def apply_coronal_metathesis(word):
    new = word[:]
    for i in range(len(word) - 1):
        new[i], new[i+1] = coronal_metathesis(word[i], word[i+1])
    return new

# Testing...
if __name__ == '__main__':
    initialize()
    #word1 = [u'a', u't', u'b', u'a', u'h', u'u', u'n', u'b', u'i']
    word1 = ['a', 'tʃ', 'b', 'a', 'h', 'u', 'n', 'b', 'i']
    print(word1)
    word2 = apply_assimilations(word1)
    print(word2)
    print(apply_coronal_metathesis(word2))
