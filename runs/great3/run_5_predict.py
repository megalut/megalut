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

	meascatpath = config.great3.path("obs", "img_%i_meascat.pkl" % subfield)
	meascat = megalut.tools.io.readpickle(config.great3.path("obs", "img_%i_meascat.pkl" % subfield))
	
	conflist = [
		("mlconfig/ada4g1.cfg", config.great3.path("ml", "%03i" % subfield, "ada4g1_sum55")),
		("mlconfig/ada4g2.cfg", config.great3.path("ml", "%03i" % subfield, "ada4g2_sum55"))
	]
	
	predcat = megalut.learn.tenbilacrun.predict(meascat, conflist)

	predcatpath = config.great3.path("pred", "img_%i_predcat.pkl" % subfield)
	megalut.tools.io.writepickle(predcat, predcatpath)
	
	
	
	"""
	cat["pre_g1"][cat["pre_g1"].mask] = 20.0
	cat["pre_g2"][cat["pre_g2"].mask] = 20.0
	
	# We cut out the columns we need
	preobscat = cat["ID","pre_g1","pre_g2"]
	
	# We write the ascii file
	preobscat.write(great3.get_path("out", "%03i.cat" % subfield), format="ascii.commented_header")
	
	logger.info("Wrote predictions cat for subfield %03i" % subfield)
	"""
	
