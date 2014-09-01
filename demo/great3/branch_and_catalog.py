"""
A demo on how to read a GREAT3 input catalog
"""

import megalut
import megalut.great3

# Optional: set the logging level. If ommited, only warnings (and worse) will be shown.
import logging
logging.basicConfig(level=logging.INFO)


# We create a Branch object:
#branch = megalut.great3.utils.Branch("control", "ground", "constant",
#	datadir="/Users/mtewes/Desktop/fake_GREAT3")
branch = megalut.great3.utils.Branch("control", "ground", "variable",
	datadir="/vol/fohlen11/fohlen11_1/mtewes/GREAT3")


print branch
print branch.stampsize()
print branch.branchdir()
print branch.psfimgfilepath(subfield=0)


# We read a galaxy catalog, that will be served as an astropy table.
cat = megalut.great3.io.readgalcat(branch, subfield=0)

print cat[:5] # Cool !
print cat.colnames
print len(cat)
print cat.meta["branch"] # The actual branch object is saved
print cat.meta["subfield"]# This as well...

megalut.utils.writepickle(cat, "cat.pkl")

# Yes, this works !
for gal in cat[:10]:
	gal["x"] *= -1

