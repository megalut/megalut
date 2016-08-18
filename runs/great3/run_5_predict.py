import os
import numpy as np

import megalut.tools as tools
import megalut.learn as learn

import config

import megalutgreat3 as mg3

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Loading the correct configuration!
great3 = mg3.great3.load_config(outdir='cgc')

# The training used by default in training is the one defined in:
# great3.trainparams_name
trainname = great3.trainparams_name
trainparamslist = great3.trainparamslist

# The simulation used by default in training is the one defined in:
# great3.simparams_name
simparams_name = great3.simparams_name

for subfield in config.subfields:
	
	# Getting the path to the correct directories
	traindir = great3.get_path("ml", "%03i" % subfield, trainname, simparams_name)
	predir = great3.get_path("pred", "%03i" % subfield, trainname, simparams_name)
	
	# We read the obs measurements
	cat = tools.io.readpickle(great3.get_path("obs", "img_%i_meascat.pkl" % subfield))
	
	# Predicting the training data
	mask= cat["adamom_g1"].mask;

	cat = learn.run.predict(cat, traindir, trainparamslist, outtweak=np.ma.median)

	# And we save the predictions
	if not os.path.exists(predir):
		os.makedirs(predir)
	
	tools.io.writepickle(cat, os.path.join(predir, "preobscat.pkl"))
	
	logger.info("Wrote predictions cat for subfield %03i" % subfield)
	
logger.info("Wrote predictions for all subfields!")
