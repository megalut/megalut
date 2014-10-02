"""
A demo that measures some moments with galsim
"""

import logging
logging.basicConfig(level=logging.DEBUG) # This time we use debug level, as an illustration

import megalut.great3
import megalut.meas

branch = megalut.great3.utils.Branch("control", "ground", "variable",
	datadir="/vol/fohlen11/fohlen11_1/mtewes/GREAT3")

subfield = 0

inputcat = megalut.great3.io.readgalcat(branch, subfield)

# These things work !
#inputcat = inputcat[:1000]
#inputcat = inputcat[inputcat["ID"] == 245007]

gridimg = megalut.gsutils.loadimg("simgalimg.fits")
meascat = megalut.meas.galsim_adamom.measure(img, inputcat, stampsize=branch.stampsize(), prefix="mes")


# To see the failed measurements:
failedcat = meascat[meascat["mes_adamom_flag"] > 0]
print failedcat

"""

# A little helper to view the stamps:
megalut.meas.galsim_adamom.pngstampgrid("failed.png", img, failedcat, stampsize=branch.stampsize(), z1=-0.3, z2=2.0)


# A scatter plot of the position residuals, as an illustration:
import matplotlib.pyplot as plt
resi_x = meascat["mes_adamom_x"] - meascat["x"]
resi_y = meascat["mes_adamom_y"] - meascat["y"]
flag = meascat["mes_adamom_flag"]
plt.scatter(resi_x, resi_y, c=flag, lw=0, s=60)
plt.show()

"""
