"""
A demo of plot.stamps.pngstampgrid()
"""

import logging
logging.basicConfig(level=logging.DEBUG)

import megalut
import megalut.plot.stamps

print "For this demo to work, run draw_and_measure_sims.py first."


img = "simgalimg.fits"
cat = megalut.tools.io.readpickle("meascat.pkl")

# Let's illustrate selecting stamps randomly:
cat = megalut.tools.table.shuffle(cat)


megalut.plot.stamps.pngstampgrid(img, cat[:20], "stamps.png", stampsize=40)

