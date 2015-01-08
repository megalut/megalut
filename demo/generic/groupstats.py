"""
A demo to test groupstats
"""

import logging
logging.basicConfig(level=logging.INFO)

import numpy as np
import astropy.table


n = 10

incats = []

for i in range(10):
	a = [0] * n
	b = np.ones(n) * i
	c = np.random.randn(n)
	cat = astropy.table.Table([a, b, c], names=('a', 'b', 'c'))
	incats.append(cat)
	

print incats[0]
