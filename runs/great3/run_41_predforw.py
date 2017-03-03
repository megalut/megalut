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

	catpath = config.great3.subpath(subfield, "simmeas", config.datasets["train-weight"], "groupmeascat.pkl")
	cat = megalut.tools.io.readpickle(catpath)
	#print megalut.tools.table.info(cat)
	#exit()
	
	traindir = config.great3.subpath(subfield, "ml", config.datasets["train-shear"])
	predcat = megalut.learn.tenbilacrun.predict(cat, config.shearconflist, traindir)

	predcatpath = config.great3.subpath(subfield, "simmeas", config.datasets["train-weight"], "groupmeascat_predforw.pkl")
	megalut.tools.io.writepickle(predcat, predcatpath)
	
	
