"""
Same as run_32, but uses weights, if available
"""

import matplotlib
matplotlib.use("AGG")

import megalut.tools
import megalut.learn
import megalut

import config
import numpy as np
import os

import plot_2_val

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)






for subfield in config.great3.subfields:

	logger.info("Working on subfield {}".format(subfield))

	
	catpath = config.great3.subpath(subfield, "simmeas", config.datasets["valid-shear"], "groupmeascat.pkl")
	cat = megalut.tools.io.readpickle(catpath)
		
	traindir = config.great3.subpath(subfield, "ml", config.datasets["train-shear"])	
	predcat = megalut.learn.tenbilacrun.predict(cat, config.shearconflist, traindir)

	if len(config.weightconflist) > 0:
		
		weighttraindir = config.great3.subpath(subfield, "ml", config.datasets["train-weight"])
		predcat = megalut.learn.tenbilacrun.predict(predcat, config.weightconflist , weighttraindir)

	
	shearconfnames = megalut.learn.tenbilacrun.confnames(config.shearconflist)
	for (confname, conf) in zip(shearconfnames, config.shearconflist):

		predcatcopy = predcat.copy() # As plots modifies it.
		
		if "s2" in conf[0] or "g2" in conf[0]:
			component = 2
		else:
			component = 1
		
		valname = "pred_{}_with_{}_{}_weights".format(config.datasets["valid-shear"], config.datasets["train-shear"], confname)
		figpredcatpath = config.great3.subpath(subfield, "val", valname + ".png")
		#figpath = config.great3.subpath(subfield, "val", "33_valw_{}.png".format(component))
		
		plot_2_val.plot(predcatcopy, component, mode="s", withweights=True, filepath=figpredcatpath)
		
	
