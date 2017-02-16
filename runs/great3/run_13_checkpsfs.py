"""
To be able to create a single training set for all branches,
we stack the starfield images into one single FITS file,
and create a single star catalog.
"""

import numpy as np
import astropy.table

import megalut
import megalutgreat3
import config

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

subfields = []
psf_adamom_g1s = []
psf_adamom_g2s = []
psf_adamom_rho4s = []
psf_adamom_sigmas = []

for (i, subfield) in enumerate(config.great3.subfields):

	catpath = config.great3.path("obs", "star_%i_meascat.pkl" % subfield)
	cat = megalut.tools.io.readpickle(catpath)
	#print megalut.tools.table.info(cat)
	
	subfields.append(subfield)
	psf_adamom_g1s.append(np.mean(cat["psf_adamom_g1"])) # measurements of 9 stars
	psf_adamom_g2s.append(np.mean(cat["psf_adamom_g2"]))
	psf_adamom_rho4s.append(np.mean(cat["psf_adamom_rho4"]))
	psf_adamom_sigmas.append(np.mean(cat["psf_adamom_sigma"]))


# We make a catalog out of this

cat = astropy.table.Table([
		subfields, psf_adamom_g1s, psf_adamom_g2s, psf_adamom_rho4s, psf_adamom_sigmas
	], names=(
		'subfield', "psf_adamom_g1", "psf_adamom_g2", "psf_adamom_rho4", "psf_adamom_sigma"
		)
	)

cat.sort("psf_adamom_sigma")

print cat


