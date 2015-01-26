"""
A demo to play with Selector
"""

import logging
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.DEBUG)

import numpy as np
import astropy.table
import megalut

# We create a table

n = 20 # number of rows

a = np.arange(n)
b = 100*np.ones(n) + np.random.randn(n) 
c = np.sqrt(np.linspace(50, 40, n))
d = np.zeros(n, dtype=int)

# To get a masked table:
cat = astropy.table.Table([a, b, c, d], names=("a", "b", "c", "d"), masked=True)
cat["c"].mask = cat["c"] < 6.5 # As an experiment, we mask some values
cat["d"].mask[3:8] = True


# To get a table without masks:
#cat = astropy.table.Table([a, b, c, d], names=("a", "b", "c", "d"))


print "Input catalog:"
print cat

sel1 = megalut.tools.table.Selector("foo", [("max", "b", 100.0), ("nomask", "c")])

sel2 = megalut.tools.table.Selector("bar", [("in", "d", -1, 2)])
# Tricky: this one used to be a bad bug. Do you want masked d values (which are zero) or not ?
# This is now fixed, masked values are rejected.

sel3 = megalut.tools.table.Selector("sel3", [("mask", "c")])

sel4 = megalut.tools.table.Selector("sel4", [("is", "d", 0)])

sel5 = megalut.tools.table.Selector("sel5", [])


print "Output catalog:"
print sel1.select(cat)

