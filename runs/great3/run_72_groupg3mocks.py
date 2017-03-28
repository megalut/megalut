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

tru_psf_g1s = []
tru_psf_g2s = []

for subfield in config.great3.subfields:
		
	predname = "pred_{}_{}".format(config.datasets["mimic-great3"], config.predcode) # Too messy to add everything here.
	predpath = config.great3.subpath(subfield, "pred", predname + ".pkl")
	
	if not os.path.exists(predpath):
		continue

	subfields.append(subfield)
	cat = megalut.tools.io.readpickle(predpath)
	
	
	tru_s1s.append(cat["tru_s1"][0])
	tru_s2s.append(cat["tru_s2"][0])
		
	pre_s1s.append(np.ma.mean(cat["pre_s1"]))
	pre_s2s.append(np.ma.mean(cat["pre_s2"]))
	
	pre_s1ws.append(np.ma.mean(cat["pre_s1"] * cat["pre_s1w"]) / np.ma.mean(cat["pre_s1w"]))
	pre_s2ws.append(np.ma.mean(cat["pre_s2"] * cat["pre_s2w"]) / np.ma.mean(cat["pre_s2w"]))
	
	psf_adamom_g1s.append(np.mean(cat["psf_adamom_g1"])) # Yes, we take the mean here. We randomly distributed the measurements of 9 stars to the galaxies.
	psf_adamom_g2s.append(np.mean(cat["psf_adamom_g2"]))
	psf_adamom_rho4s.append(np.mean(cat["psf_adamom_rho4"]))
	psf_adamom_sigmas.append(np.mean(cat["psf_adamom_sigma"]))


	# We also need to read in the true PSF orientations (as measurements fail, sometimes)
	trustarpath = config.great3.trustarfilepath(subfield)
	trustar = megalutgreat3.io.readshear(trustarpath)
	assert len(trustar) == 4 # epoch_index psf_g1 psf_g2 subfield_index 
	assert int(subfield) == int(trustar[3])
	
	# Some of this PSF info was flagged, this is how they deal with it in the GREAT3 (SAD!)
	# We need to do the same, to reproduce GREAT3 metrics exactly.
	if trustar[1] < -9.9:
		trustar[1] = 0.0
	if trustar[2] < -9.9:
		trustar[2] = 0.0
	tru_psf_g1s.append(trustar[1])
	tru_psf_g2s.append(trustar[2])



# We make a catalog out of this

cat = astropy.table.Table([
		subfields, tru_s1s, tru_s2s, pre_s1s, pre_s2s, pre_s1ws, pre_s2ws,
		psf_adamom_g1s, psf_adamom_g2s, psf_adamom_rho4s, psf_adamom_sigmas,
		tru_psf_g1s, tru_psf_g2s
	], names=(
		'subfield', 'tru_s1', 'tru_s2', "pre_s1", "pre_s2", "pre_s1w", "pre_s2w",
		"psf_adamom_g1", "psf_adamom_g2", "psf_adamom_rho4", "psf_adamom_sigma",
		"tru_psf_g1", "tru_psf_g2"
		)
	)


#print megalut.tools.table.info(cat)
catpath = config.great3.path("{}_summary_{}.pkl".format(config.datasets["mimic-great3"], config.predcode))
cat = megalut.tools.io.writepickle(cat, catpath)
