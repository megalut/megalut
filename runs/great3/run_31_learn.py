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

import plot_2_val

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)


"""
conflist = []
if "1" in config.runcomp:
	conflist.append(("mlconfig/ada4s1.cfg", "mlconfig/sum55.cfg"))
if "2" in config.runcomp:
	conflist.append(("mlconfig/ada4s2.cfg", "mlconfig/sum55.cfg"))

"""

select = True


for subfield in config.great3.subfields:
	
	
	logger.info("Working on subfield {}".format(subfield))
	
	# Getting the path to the correct directories
	measdir = config.great3.subpath(subfield, "simmeas", config.datasets["train-shear"])
	traindir = config.great3.subpath(subfield, "ml", config.datasets["train-shear"])
	
	# And to the catalogue
	traincatpath = os.path.join(measdir, "groupmeascat.pkl")
	cat = megalut.tools.io.readpickle(traincatpath)
	#print megalut.tools.table.info(cat)
	
	if select:
		s = megalut.tools.table.Selector("fortrain", [
			("max", "adamom_failfrac", 0.1),
		])
		cat = s.select(cat)
	
	#exit()	
	#print megalut.tools.table.info(cat)
	
	
	# Running the training
	dirnames = megalut.learn.tenbilacrun.train(cat, config.shearconflist, traindir)
	
	# And saving a summary plot next to the tenbilac working directories
	for dirname in dirnames:
		tenbilacdirpath = os.path.join(traindir, dirname)
		ten = tenbilac.com.Tenbilac(tenbilacdirpath)
		ten._readmembers()
		tenbilac.plot.summaryerrevo(ten.committee, filepath=os.path.join(traindir, "{}_summary.png".format(dirname)))
	
	
	#dirnames = ["ada4s1_sum55"]
	#dirnames = megalut.learn.tenbilacrun.confnames(conflist)
	# Self-predicting
	
	cat = megalut.tools.io.readpickle(traincatpath) # To get the full catalog with all cases, not just the selected ones
	for (dirname, conf) in zip(dirnames, config.shearconflist):

		predcat = megalut.learn.tenbilacrun.predict(cat, [conf], traindir)
		predcatpath = os.path.join(traindir, "{}_selfpred.pkl".format(dirname))
		megalut.tools.io.writepickle(predcat, predcatpath)
		figpredcatpath = os.path.join(traindir, "{}_selfpred.png".format(dirname))
		
		if "s2" in conf[0] or "g2" in conf[0]:
			component = 2
		else:
			component = 1
		plot_2_val.plot(predcat, component, mode=config.trainmode, filepath=figpredcatpath)
	
	
	
