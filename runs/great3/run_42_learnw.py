import matplotlib
matplotlib.use("AGG")


import megalut.tools
import megalut.learn
import megalut
import tenbilac

import config
import numpy as np
import os

import plot_3_valw


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)



for subfield in config.great3.subfields:
	
	
	logger.info("Working on subfield {}".format(subfield))
	
	# Getting the path to the correct directories
	measdir = config.great3.subpath(subfield, "simmeas", config.datasets["train-weight"])
	traindir = config.great3.subpath(subfield, "ml", config.datasets["train-weight"])
	
	# And to the catalogue
	traincatpath = os.path.join(measdir, "groupmeascat_predforw.pkl")
	cat = megalut.tools.io.readpickle(traincatpath)
	
	# Running the training	
	dirnames = megalut.learn.tenbilacrun.train(cat, config.weightconflist, traindir)
	
	
	# Summary plot and self-predictions
	for dirname in dirnames:
		tenbilacdirpath = os.path.join(traindir, dirname)
		ten = tenbilac.com.Tenbilac(tenbilacdirpath)
		ten._readmembers()
		tenbilac.plot.summaryerrevo(ten.committee, filepath=os.path.join(traindir, "{}_summary.png".format(dirname)))


	cat = megalut.tools.io.readpickle(traincatpath) # To get the full catalog with all cases	
	
	for (dirname, conf) in zip(dirnames, config.weightconflist):

		predcat = megalut.learn.tenbilacrun.predict(cat, [conf], traindir)
		predcatpath = os.path.join(traindir, "{}_selfpred.pkl".format(dirname))
		megalut.tools.io.writepickle(predcat, predcatpath)
		figpredcatpath = os.path.join(traindir, "{}_selfpred.png".format(dirname))
		
		if "s2" in conf[0] or "g2" in conf[0]:
			component = 2
		else:
			component = 1
		plot_3_valw.plot(predcat, component, filepath=figpredcatpath)
			
