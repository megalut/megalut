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

	for conf in config.shearconflist: # We go through them one by one here.

		catpath = config.great3.subpath(subfield, "simmeas", config.datasets["valid-shear"], "groupmeascat.pkl")
		cat = megalut.tools.io.readpickle(catpath)
		traindir = config.great3.subpath(subfield, "ml", config.datasets["train-shear"])

		confname = megalut.learn.tenbilacrun.confnames([conf])[0]
		predcat = megalut.learn.tenbilacrun.predict(cat, [conf], traindir)

		valname = "pred_{}_with_{}_{}".format(config.datasets["valid-shear"], config.datasets["train-shear"], confname)	

		predcatpath = config.great3.subpath(subfield, "val", valname + ".pkl")
		figpredcatpath = config.great3.subpath(subfield, "val", valname + ".png")
		
		figgoodpredcatpath = config.great3.subpath(subfield, "val", valname + "_good.png")
		predcat2 = predcat.copy()
			
		megalut.tools.io.writepickle(predcat, predcatpath)
	
		# And make the plot	
		if "s2" in conf[0] or "g2" in conf[0]:
			component = 2
		else:
			component = 1
		plot_2_val.plot(predcat, component, mode="s", filepath=figpredcatpath)
		
		s = megalut.tools.table.Selector("good", [
			("max", "pre_maskedfrac", 0.1),
		])
		plot_2_val.plot(predcat2, component, mode="s", select=s, filepath=figgoodpredcatpath)
	
	"""
	conflist = [
		#("mlconfig/ada4s1.cfg", config.great3.path("ml", "%03i" % subfield, trainspname, "ada4s1_sum55")),
		#("mlconfig/ada4s1.cfg", config.great3.path("ml", "%03i" % subfield, trainspname, "ada4s1_sum55/mini_ada4s1_sum55_2017-02-26T09-46-42")),
	]
	"""
	
