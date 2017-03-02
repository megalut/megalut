import matplotlib
matplotlib.use("AGG")


import megalut.tools
import megalut.learn
import megalut
import tenbilac

import config
import numpy as np
import os

from megalut.tools.feature import Feature
import matplotlib.pyplot as plt

import plot_2_valid

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)
#tbllogger = logging.getLogger("tenbilac")


spname = "G3CGCSersics_train_nn"
#spname = "G3CGCSersics_train_100rea"
#spname = "G3CGCSersics_train_shear_snc100"
#spname = "G3CGCSersics_train_shear_snc10000"
#spname = "G3CGCSersics_train_nn_2rea"
#spname = "G3CGCSersics_train_nn_20rea"
#spname = "G3CGCSersics_train_shear_snc100_nn"
#spname = "G3CGCSersics_train_shear_snc100_nn_G3"


select = True

conflist = [
	("mlconfig/ada4g1.cfg", "mlconfig/sum55.cfg"),
	#("mlconfig/ada4g2.cfg", "mlconfig/sum55.cfg"),
	#("mlconfig/ada4s1.cfg", "mlconfig/sum55.cfg"),
	
]


for subfield in config.great3.subfields:
	
	
	logger.info("Working on subfield {}".format(subfield))
	
	# Getting the path to the correct directories
	measdir = config.great3.path("simmeas","%03i" % subfield, spname)
	traindir = config.great3.path("ml", "%03i" % subfield, spname)
	
	# And to the catalogue
	traincatpath = os.path.join(measdir, "groupmeascat.pkl")
	cat = megalut.tools.io.readpickle(traincatpath)
	#print megalut.tools.table.info(cat)
	
	if select:
		
		cat["meas_frac"] = (float(cat["adamom_g1"].shape[1]) - np.sum(cat["adamom_g1"].mask, axis=1))/float(cat["adamom_g1"].shape[1])
		s = megalut.tools.table.Selector("fortrain", [
			("min", "meas_frac", 0.9),
		])
		cat = s.select(cat)
	
	#exit()	
	#print megalut.tools.table.info(cat)
	
	"""
	# Running the training
	dirnames = megalut.learn.tenbilacrun.train(cat, conflist, traindir)
	
	# And saving a summary plot next to the tenbilac working directories
	for dirname in dirnames:
		tenbilacdirpath = os.path.join(traindir, dirname)
		ten = tenbilac.com.Tenbilac(tenbilacdirpath)
		ten._readmembers()
		tenbilac.plot.summaryerrevo(ten.committee, filepath=os.path.join(traindir, "{}_summary.png".format(dirname)))
	
	"""
	dirnames = ["ada4g1_sum55"]
	
	# Self-predicting
	
	cat = megalut.tools.io.readpickle(traincatpath) # To get the full catalog with all cases
	for (dirname, conf) in zip(dirnames, conflist):

		predcat = megalut.learn.tenbilacrun.predict(cat, [conf], traindir)
		predcatpath = os.path.join(traindir, "{}_selfpred.pkl".format(dirname))
		megalut.tools.io.writepickle(predcat, predcatpath)
		figpredcatpath = os.path.join(traindir, "{}_selfpred.png".format(dirname))
		
		if "s2" in conf[0] or "g2" in conf[0]:
			component = 2
		else:
			component = 1
		plot_2_valid.plot(predcat, component, mode=config.trainmode, filepath=figpredcatpath)
	
	
	
