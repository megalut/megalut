"""
A minimal demo about drawing simulated galaxies
"""

import logging
logging.basicConfig(level=logging.DEBUG)

import megalut
import megalut.sim


# First, we set the desired distributions of parameters, by overwriting the default distributions.

class Mysimparams(megalut.sim.params.Params):
	def get_flux(self):
		return 120.0
		
mysimparams = Mysimparams()

simcat = megalut.sim.stampgrid.drawcat(mysimparams, n=10)

print simcat[:5]

# Now, we pass this catalog to drawimg, to generate the actual FITS image.

megalut.sim.stampgrid.drawimg(simcat, stampsize=48,
	simgalimgfilepath="simgalimg.fits",
	simtrugalimgfilepath="simtrugalimg.fits",
	simpsfimgfilepath="simpsfimg.fits"
	)

