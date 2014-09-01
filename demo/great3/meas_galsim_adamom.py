"""
A demo that measures some moments with galsim
"""

import logging
logging.basicConfig(level=logging.DEBUG)

import megalut
import megalut.great3
import megalut.meas

branch = megalut.great3.utils.Branch("control", "ground", "variable",
	datadir="/vol/fohlen11/fohlen11_1/mtewes/GREAT3")

subfield = 0

inputcat = megalut.great3.io.readgalcat(branch, subfield)

#inputcat = inputcat[:1000]
#inputcat = inputcat[inputcat["ID"] == 245007]

meascat = megalut.meas.galsim_adamom.measure(branch.galimgfilepath(subfield), inputcat, stampsize=branch.stampsize())

print meascat


# A scatter plot, as an illustration:

import matplotlib.pyplot as plt
import numpy as np
resi_x = meascat["mes_adamom_x"] - meascat["x"]
resi_y = meascat["mes_adamom_y"] - meascat["y"]
c = meascat["mes_adamom_flag"]
plt.scatter(resi_x, resi_y, c=c, lw=0, s=60)
plt.show()


