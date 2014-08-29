"""
A demo on how to read a GREAT3 input catalog
"""

import megalut
import megalut.great3
import megalut.meas

branch = megalut.great3.utils.Branch("control", "ground", "variable",
	datadir="/vol/fohlen11/fohlen11_1/mtewes/GREAT3")

subfield = 0

inputcat = megalut.great3.io.readgalcat(branch, subfield)

meascat = megalut.meas.galsim_adamom.measure(branch.galimgfilepath(subfield), inputcat, stampsize=branch.stampsize())

meascat.write("meascat.pkl")

for gal in meascat.data.values()[:5]:
	print gal.fields

