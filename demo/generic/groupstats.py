"""
A demo to play with groupstats
"""

import logging
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.DEBUG)

import numpy as np
import astropy.table
import megalut

# First we make a bunch of catalogs to play with:

n = 10 # number of rows
incats = []

for i in range(5):
	a = [0] * n
	b = np.ones(n) * i
	c = np.random.randn(n)
	cat = astropy.table.Table([a, b, c], names=("a", "b", "c"), masked=True)
	cat["c"].mask = cat["c"] < 0.5 # As an experiment, we mask many values
	incats.append(cat)
	

print "Some input catalogs:"
print incats[0]
print incats[1]
print incats[-1]


# And we call groupstats (you can try out both):

#groupcat = megalut.tools.table.groupstats(incats, groupcols=["b"], removecols=["c"], removereas=True, keepfirstrea=True)
groupcat = megalut.tools.table.groupstats(incats, groupcols=["b", "c"], removecols=["a"], removereas=False)


print "The output:"
print groupcat

print groupcat["b_mean"].meta
