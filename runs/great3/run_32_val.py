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


#valspname = "G3CGCSersics_valid"
#valspname = "G3CGCSersics_statshear"

valspname = "G3CGCSersics_valid_shear_snc1000_G3"  # <--- to validate shear
#valspname = "G3CGCSersics_valid_overall" # <--- to validate overall, with weights

trainspname = "G3CGCSersics_train_nn"
#trainspname = "G3CGCSersics_train_shear_snc100"
#trainspname = "G3CGCSersics_train_shear_snc10000"
#trainspname = "G3CGCSersics_train_nn_2rea"
#trainspname = "G3CGCSersics_train_nn_20rea"
#trainspname = "G3CGCSersics_train_shear_snc100_nn"
#trainspname = "G3CGCSersics_train_shear_snc100_nn_G3"


# Select a new


predname = "ada4_sum55_statshear"
#predname = "ada4_sum55_statshear_20000its"

#predname = "ada4_sum55_valid_weights"



for subfield in config.great3.subfields:

	logger.info("Working on subfield {}".format(subfield))

	catpath = config.great3.path("simmeas", "%03i" % subfield, valspname, "groupmeascat.pkl")
	cat = megalut.tools.io.readpickle(catpath)
	#print megalut.tools.table.info(cat)
	
	conflist = [
		#("mlconfig/ada4s1.cfg", config.great3.path("ml", "%03i" % subfield, trainspname, "ada4s1_sum55")),
		("mlconfig/ada4g1.cfg", config.great3.path("ml", "%03i" % subfield, trainspname, "ada4g1_sum55")),
		
		#("mlconfig/ada4s1.cfg", config.great3.path("ml", "%03i" % subfield, trainspname, "ada4s1_sum55")),
		#("mlconfig/ada4s1.cfg", config.great3.path("ml", "%03i" % subfield, trainspname, "ada4s1_sum55/mini_ada4s1_sum55_2017-02-26T09-46-42")),
		
		
		#("mlconfig/ada4g2.cfg", config.great3.path("ml", "%03i" % subfield, trainspname, "ada4g2_sum55")),
		#("mlconfig/ada2g1w.cfg", config.great3.path("ml", "%03i" % subfield, trainspname, "ada2g1w_sum33w")),

		
	]
	
	
	predcat = megalut.learn.tenbilacrun.predict(cat, conflist)

	predcatpath = config.great3.path("ml", "%03i" % subfield, trainspname, "predcat_{}.pkl".format(predname))
	megalut.tools.io.writepickle(predcat, predcatpath)
	
	
