"""
A demo that measures some moments with galsim
"""

import logging
logging.basicConfig(level=logging.INFO)

import megalut
import megalut.great3
import megalut.meas

branch = megalut.great3.utils.Branch("control", "ground", "variable",
	datadir="/vol/fohlen11/fohlen11_1/mtewes/GREAT3")

subfield = 0

inputcat = megalut.great3.io.readgalcat(branch, subfield)

inputcat = inputcat[:10]

print inputcat.meta

#meascat = megalut.meas.galsim_adamom.measure(branch.galimgfilepath(subfield), inputcat, stampsize=branch.stampsize())

#print meascat[:5]

#megalut.utils.writepickle(meascat, "meascat.pkl")

