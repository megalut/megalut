"""
A small demo with astropy.tables and our own tools.table.hjoin function.
You can test the safety checks by tweaking the tables:
- Try modifying of of the myid in one of the tables
- Try keys=None in join()
"""

import logging
logging.basicConfig(level=logging.INFO)

import megalut.tools
import astropy.table


cat1 = """
myid   x       y      mag
a      1.0     1.0    22.0
b      1.0     2.0    23.0
c      1.0     3.0    24.0
"""
cat1 = astropy.table.Table.read(cat1, format='ascii')


cat2 = """
myid   g1      g2    mag
b     -0.1     0.1   23.0
a      0.1    -0.2   22.0
c      0.2     0.1   24.0
"""
cat2 = astropy.table.Table.read(cat2, format='ascii')

print "cat1:"
print cat1
print "cat2:"
print cat2

print "-" * 100
print "Playing with astropy.table.join():"
print astropy.table.join(cat1, cat2, keys="myid", join_type='left')


print "-" * 100
print "hjoin:"
print megalut.tools.table.hjoin(cat1, cat2, "myid")




