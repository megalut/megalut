import matplotlib
matplotlib.use("AGG")

import megalut.tools
import megalut.learn
import megalut

import config
import numpy as np
import os

import plot_3_valw

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)



for subfield in config.great3.subfields:

	logger.info("Working on subfield {}".format(subfield))

	catpath = config.great3.subpath(subfield, "simmeas", config.datasets["mimic-great3"], "groupmeascat.pkl")
	
	if not os.path.exists(catpath):
		continue
	
	cat = megalut.tools.io.readpickle(catpath)
	#print cat["tru_rad", "tru_read_noise", "psf_adamom_g1", "tru_s1", "tru_g1"]
	#print megalut.tools.table.info(cat)
	#exit()
	
	sheartraindir = config.great3.subpath(subfield, "ml", config.datasets["train-shear"])
	cat = megalut.learn.tenbilacrun.predict(cat, config.shearconflist , sheartraindir)
	
	if len(config.weightconflist) > 0:
		
		weighttraindir = config.great3.subpath(subfield, "ml", config.datasets["train-weight"])
		cat = megalut.learn.tenbilacrun.predict(cat, config.weightconflist , weighttraindir)
		
	
	predname = "pred_{}_{}".format(config.datasets["mimic-great3"], config.predcode) # Too messy to add everything here.
	predpath = config.great3.subpath(subfield, "pred", predname + ".pkl")
	megalut.tools.io.writepickle(cat, predpath)

