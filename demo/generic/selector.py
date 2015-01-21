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

# To get a masked table:
cat = astropy.table.Table([a, b, c], names=("a", "b", "c"), masked=True)
cat["c"].mask = cat["c"] < 6.5 # As an experiment, we mask some values

# To get a table without masks:
#cat = astropy.table.Table([a, b, c], names=("a", "b", "c"))


print "Input catalog:"
print cat

sel = megalut.tools.table.Selector("foo", [("max", "b", 100.0), ("nomask", "c")])


print "Output catalog:"
print sel.select(cat)

