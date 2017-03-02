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


valspname = "G3CGCSersics_valid_overall" # <--- to validate overall, with weights

predname = "test1"



for subfield in config.great3.subfields:

	logger.info("Working on subfield {}".format(subfield))

	catpath = config.great3.path("simmeas", "%03i" % subfield, valspname, "groupmeascat.pkl")
	cat = megalut.tools.io.readpickle(catpath)
	#print megalut.tools.table.info(cat)
	
	conflist = [
			
		("mlconfig/ada4s1.cfg", config.great3.path("ml", "%03i" % subfield, "G3CGCSersics_train_shear_snc100_nn_G3", "ada4s1_sum55")),
		("mlconfig/ada2s1w.cfg", config.great3.path("ml", "%03i" % subfield, "G3CGCSersics_statshear", "ada2s1w_sum3w")),
		
	]
	
	predcat = megalut.learn.tenbilacrun.predict(cat, conflist)

	#print np.sum(predcat["pre_s1"].mask)
	#exit()

	valdir = config.great3.path("val", "%03i" % subfield)
	if not os.path.isdir(valdir):
		os.makedirs(valdir)
	predcatpath = os.path.join(valdir, "predcat_{}.pkl".format(predname))
	megalut.tools.io.writepickle(predcat, predcatpath)
	
	
