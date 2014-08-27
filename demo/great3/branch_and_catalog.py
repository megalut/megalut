"""
A demo on how to read a GREAT3 input catalog
"""

import megalut
import megalut.great3


branch = megalut.great3.utils.Branch("control", "ground", "variable",
	datadir="/vol/fohlen11/fohlen11_1/mtewes/GREAT3")

#print branch.gets()
#print branch.branchdir()
#print branch.obsgalcatfilepath(subfield=0)

cat = megalut.great3.io.readgalcat(branch, subfield=0)


print cat
print cat.meta["branch"] # The actual branch object is saved

#for gal in cat.galaxies.values():
#	print gal

