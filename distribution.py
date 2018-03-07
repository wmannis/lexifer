#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Revision: 1.1 $
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


import random

# When you are selecting from a pool a *lot*, this
# will speed things up a bit.  Takes a dict of keys
# and weights.
class WeightedSelector(object):
    __slots__ = ['keys', 'weights', 'sum', 'n']
    
    def __init__(self, dic):
        # build parallel arrays for indexing
        self.keys = []
        self.weights = []
        for key, weight in dic.iteritems():
            self.keys.append(key)
            self.weights.append(weight)
        self.sum = sum(self.weights) - 1
        self.n = len(self.keys)

    def select(self):
        pick = random.uniform(0, self.sum)
        tmp = 0
        for i in range(self.n):
            tmp += self.weights[i]
            if pick < tmp:
                return self.keys[i]

    def __iter__(self):
        return iter(self.keys)

#m = WeightedSelector({'a': 7, 'b': 5, 'c': 1})
#for i in range(10):
#	print(m.select())
