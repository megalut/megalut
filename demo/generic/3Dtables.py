"""
A demo to play with 3D astropy tables, basically to see if and how they work before adopting them.
"""

import logging
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.DEBUG)

import numpy as np
import astropy.table
#import megalut


print "Astropy version ", astropy.__version__

from astropy.table import Table, Column, MaskedColumn


nrow = 4
nrea = 10

carr = np.random.randn(nrow * nrea).reshape((nrow, nrea))


a = Column([1, 2, 3, 4], name='a')
b = Column([1.3, 2.3, 3.3, 4.3], name='b')
c = MaskedColumn(carr, name='c')

t = Table((a, b, c), masked=True)


print t["c"].mask

#exit()

t["c"].mask[0, 0] = True


print t


print t["c"].data

