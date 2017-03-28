import matplotlib
matplotlib.use("AGG")

import megalut.tools
import megalut.learn
import megalut

import config
import numpy as np
import os


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)



for subfield in config.great3.subfields:

	logger.info("Working on subfield {}".format(subfield))

	meascatpath = config.great3.subpath(subfield, "obs", "img_meascat.pkl")
	cat = megalut.tools.io.readpickle(meascatpath)
	
	# Predicting shear
	traindir = config.great3.subpath(subfield, "ml", config.datasets["train-shear"])
	cat = megalut.learn.tenbilacrun.predict(cat, config.shearconflist, traindir)

	# Predicting weight
	traindir = config.great3.subpath(subfield, "ml", config.datasets["train-weight"])
	cat = megalut.learn.tenbilacrun.predict(cat, config.weightconflist, traindir)

	
	predcatpath = config.great3.subpath(subfield, "pred", "predcat_{}.pkl".format(config.predcode))
	megalut.tools.io.writepickle(cat, predcatpath)
	

	"""
	# If predictions are masked, put them to 20 and weights to 0:	
	cat["pre_s1"][cat["pre_s1"].mask] = 20.0
	cat["pre_s2"][cat["pre_s2"].mask] = 20.0
	cat["pre_s1w"][cat["pre_s1"].mask] = 0.0
	cat["pre_s2w"][cat["pre_s2"].mask] = 0.0

	cat["pre_s1"][cat["pre_s1w"].mask] = 20.0
	cat["pre_s2"][cat["pre_s2w"].mask] = 20.0
	cat["pre_s1w"][cat["pre_s1w"].mask] = 0.0
	cat["pre_s2w"][cat["pre_s2w"].mask] = 0.0
	
	
	# We cut out the columns we need
	preobscat = cat["ID","pre_s1","pre_s1w", "pre_s2","pre_s2w"]
	
	# We write the ascii file
	preobscat.write(great3.subpath(subfield, "out", "%03i.cat" % subfield), format="ascii.commented_header")
	
	logger.info("Wrote predictions cat for subfield %03i" % subfield)
	"""
