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
  (u'p', u'p', 'voiceless', 'bilabial', 'stop'),
  (u'b', u'b', 'voiced', 'bilabial', 'stop'),
  (u'ɸ', u'ph', 'voiced', 'bilabial', 'fricative'),
  (u'β', u'bh', 'voiced', 'bilabial', 'fricative'),
  (u'f', u'f', 'voiceless', 'labiodental', 'fricative'),
  (u'v', u'v', 'voiced', 'labiodental', 'fricative'),
  (u'm', u'm', 'voiced', 'bilabial', 'nasal'),
  (u'm', u'm', 'voiced', 'labiodental', 'nasal'),
  # Alveolar
  (u't', u't', 'voiceless', 'alveolar', 'stop'),
  (u'd', u'd', 'voiced', 'alveolar', 'stop'),
  (u's', u's', 'voiceless', 'alveolar', 'sibilant'),
  (u'z', u'z', 'voiced', 'alveolar', 'sibilant'),
  (u'θ', u'th', 'voiceless', 'alveolar', 'fricative'),
  (u'ð', u'dh', 'voiced', 'alveolar', 'fricative'),
  (u'ɬ', u'lh', 'voiceless', 'alveolar', 'lateral fricative'),
  (u'ɮ', u'ldh', 'voiced', 'alveolar', 'lateral fricative'),
  (u'tɬ', u'tl', 'voiceless', 'alveolar', 'lateral affricate'),
  (u'dɮ', u'dl', 'voiced', 'alveolar', 'lateral affricate'),
  (u'ts', u'ts', 'voiceless', 'alveolar', 'affricate'),
  (u'dz', u'dz', 'voiced', 'alveolar', 'affricate'),
  (u'ʃ', u'sh', 'voiceless', 'postalveolar', 'sibilant'),
  (u'ʒ', u'zh', 'voiced', 'postalveolar', 'sibilant'),
  (u'tʃ', u'ch', 'voiceless', 'postalveolar', 'affricate'),
  (u'dʒ', u'j', 'voiced', 'postalveolar', 'affricate'),
  (u'n', u'n', 'voiced', 'alveolar', 'nasal'),
  # Retroflex
  (u'ʈ', u'rt', 'voiceless', 'retroflex', 'stop'),
  (u'ɖ', u'rd', 'voiced', 'retroflex', 'stop'),
  (u'ʂ', u'sr', 'voiceless', 'retroflex', 'sibilant'),
  (u'ʐ', u'zr', 'voiced', 'retroflex', 'sibilant'),
  (u'ʈʂ', u'rts', 'voiceless', 'retroflex', 'affricate'),
  (u'ɖʐ', u'rdz', 'voiced', 'retroflex', 'affricate'),
  (u'ɳ', u'rn', 'voiced', 'retroflex', 'nasal'),
  # Velar
  (u'k', u'k', 'voiceless', 'velar', 'stop'),
  (u'g', u'k', 'voiced', 'velar', 'stop'),
  (u'x', u'kh', 'voiceless', 'velar', 'fricative'),
  (u'ɣ', u'gh', 'voiced', 'velar', 'fricative'),
  (u'ŋ', u'ng', 'voiced', 'velar', 'nasal'),
  # Uvular
  (u'q', u'q', 'voiceless', 'uvular', 'stop'),
  (u'ɢ', u'gq', 'voiced', 'uvular', 'stop'),
  (u'χ', u'qh', 'voiceless', 'uvular', 'fricative'),
  (u'ʁ', u'gqh', 'voiced', 'uvular', 'fricative'),
  (u'ɴ', u'nq', 'voiced', 'uvular', 'nasal')]


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
        raise Error, "Unknown notation: %s" % notation
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
    word1 = [u'a', u'tʃ', u'b', u'a', u'h', u'u', u'n', u'b', u'i']
    print word1
    word2 = apply_assimilations(word1)
    print word2
    print apply_coronal_metathesis(word2)
