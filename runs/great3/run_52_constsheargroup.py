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
tru_s1s = []
tru_s2s = []
pre_s1s = []
pre_s2s = []
pre_s1ws = [] # Not for the weights, but for the weighted averages!
pre_s2ws = []


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
	tru_s1s.append(trushear[0])
	tru_s2s.append(trushear[1])
	
	
	# Reading estimate catalogs
	predcatpath = config.great3.subpath(subfield, "pred", "predcat_{}.pkl".format(config.predcode))
	cat = megalut.tools.io.readpickle(predcatpath)
	
	#print megalut.tools.table.info(cat)
	#exit()
	
	pre_s1s.append(np.mean(cat["pre_s1"]))
	pre_s2s.append(np.mean(cat["pre_s2"]))
	
	pre_s1ws.append(np.ma.mean(cat["pre_s1"] * cat["pre_s1w"]) / np.ma.mean(cat["pre_s1w"]))
	pre_s2ws.append(np.ma.mean(cat["pre_s2"] * cat["pre_s2w"]) / np.ma.mean(cat["pre_s2w"]))
	
	psf_adamom_g1s.append(np.mean(cat["psf_adamom_g1"])) # Yes, we take the mean here. We randomly distributed the measurements of 9 stars to the galaxies.
	psf_adamom_g2s.append(np.mean(cat["psf_adamom_g2"]))
	psf_adamom_rho4s.append(np.mean(cat["psf_adamom_rho4"]))
	psf_adamom_sigmas.append(np.mean(cat["psf_adamom_sigma"]))


# We make a catalog out of this

cat = astropy.table.Table([
		subfields, tru_s1s, tru_s2s, pre_s1s, pre_s2s, pre_s1ws, pre_s2ws,
		psf_adamom_g1s, psf_adamom_g2s, psf_adamom_rho4s, psf_adamom_sigmas
	], names=(
		'subfield', 'tru_s1', 'tru_s2', "pre_s1", "pre_s2", "pre_s1w", "pre_s2w",
		"psf_adamom_g1", "psf_adamom_g2", "psf_adamom_rho4", "psf_adamom_sigma"
		)
	)


#print megalut.tools.table.info(cat)
catpath = config.great3.path("summary_{}.pkl".format(config.predcode))
cat = megalut.tools.io.writepickle(cat, catpath)
