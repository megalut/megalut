"""
A minimal demo about drawing simulated galaxies
"""

import logging
logging.basicConfig(level=logging.INFO)

import megalut.sim
import megalut.meas

# First, we set the desired distributions of parameters, by overwriting the default distributions.

class MySimParams(megalut.sim.params.Params):
	def get_flux(self):
		return 300.0
		
mysimparams = MySimParams()


# We make a catalog of 100 x 100 simulated galaxies :

simcat = megalut.sim.stampgrid.drawcat(mysimparams, n=10, stampsize=48)


# Now, we pass this catalog to drawimg, to generate the actual simulated images.

megalut.sim.stampgrid.drawimg(simcat, 
	simgalimgfilepath="simgalimg.fits",
	simtrugalimgfilepath="simtrugalimg.fits",
	simpsfimgfilepath="simpsfimg.fits"
	)

# We can directly proceed by measuring the images

gridimg = megalut.gsutils.loadimg("simgalimg.fits")
meascat = megalut.meas.galsim_adamom.measure(gridimg, simcat, stampsize=48, prefix="mes")

# meascat is the output catalog, it contains the measured features:
print meascat[:5]

# We save it into a pickle
megalut.utils.writepickle(meascat, "meascat.pkl")

# Let's make a simple comparision plot:
import matplotlib.pyplot as plt
resi_x = meascat["mes_x"] - meascat["x"]
resi_y = meascat["mes_y"] - meascat["y"]
flag = meascat["mes_flag"]
plt.scatter(resi_x, resi_y, c=flag, lw=0, s=30)
plt.xlabel("mes_x residual")
plt.ylabel("mes_y residual")
plt.show()


