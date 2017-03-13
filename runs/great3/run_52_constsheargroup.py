#import matplotlib
#matplotlib.use("AGG")

import megalut
import megalut.tools
import megalutgreat3
import astropy


import config
import numpy as np
import os


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)



subfields = []
tru_g1s = []
tru_g2s = []
pre_g1s = []
pre_g2s = []
psf_adamom_g1s = []
psf_adamom_g2s = []
psf_adamom_rho4s = []
psf_adamom_sigmas = []

for subfield in config.great3.subfields:
	
	subfields.append(subfield)

	# Reading truth
	trushearpath = config.great3.trushearfilepath(subfield)
	trushear = megalutgreat3.io.readshear(trushearpath)
	assert len(trushear) == 2
	tru_g1s.append(trushear[0])
	tru_g2s.append(trushear[1])
	
	
	# Reading estimate catalogs
	predcatpath = config.great3.path("pred", "img_%i_predcat.pkl" % subfield)
	cat = megalut.tools.io.readpickle(predcatpath)
	
	#print megalut.tools.table.info(cat)
	pre_g1s.append(np.mean(cat["pre_g1_adamom"]))
	pre_g2s.append(np.mean(cat["pre_g2_adamom"]))

	psf_adamom_g1s.append(np.mean(cat["psf_adamom_g1"])) # Yes, we take the mean here. We randomly distributed the measurements of 9 stars to the galaxies.
	psf_adamom_g2s.append(np.mean(cat["psf_adamom_g2"]))
	psf_adamom_rho4s.append(np.mean(cat["psf_adamom_rho4"]))
	psf_adamom_sigmas.append(np.mean(cat["psf_adamom_sigma"]))


# We make a catalog out of this

cat = astropy.table.Table([
		subfields, tru_g1s, tru_g2s, pre_g1s, pre_g2s,
		psf_adamom_g1s, psf_adamom_g2s, psf_adamom_rho4s, psf_adamom_sigmas
	], names=(
		'subfield', 'tru_g1', 'tru_g2', "pre_g1", "pre_g2",
		"psf_adamom_g1", "psf_adamom_g2", "psf_adamom_rho4", "psf_adamom_sigma"
		)
	)


#print megalut.tools.table.info(cat)
catpath = config.great3.path("pred", "summary_cat.pkl")
cat = megalut.tools.io.writepickle(cat, catpath)
