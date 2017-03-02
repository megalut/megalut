import matplotlib
matplotlib.use("AGG")


import megalut.tools
import megalut.learn
import megalut
import tenbilac

import config
import numpy as np
import os

import plot_3_validw


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)
#tbllogger = logging.getLogger("tenbilac")


spname = "G3CGCSersics_statshear"

conflist = [
	("mlconfig/ada2s1w.cfg", "mlconfig/sum3w.cfg"),
	#("mlconfig/ada2s1w.cfg", "mlconfig/sum33w.cfg"),
]

selfpredict = True


for subfield in config.great3.subfields:
	
	
	logger.info("Working on subfield {}".format(subfield))
	
	# Getting the path to the correct directories
	measdir = config.great3.path("simmeas","%03i" % subfield, spname)
	traindir = config.great3.path("ml", "%03i" % subfield, spname)
	
	# And to the catalogue
	traincatpath = os.path.join(measdir, "groupmeascat_pred.pkl")
	traincat = megalut.tools.io.readpickle(traincatpath)
	
	# Running the training	
	#dirnames = megalut.learn.tenbilacrun.train(traincat, conflist, traindir)
	dirnames = ["ada2s1w_sum3w"]
	
	
	# Summary plot and self-predictions
	
	traincat = megalut.tools.io.readpickle(traincatpath) # To get the full catalog with all cases	
	for (dirname, conf) in zip(dirnames, conflist):

		tenbilacdirpath = os.path.join(traindir, dirname)
		ten = tenbilac.com.Tenbilac(tenbilacdirpath)
		ten._readmembers()
		tenbilac.plot.summaryerrevo(ten.committee, filepath=os.path.join(traindir, "{}_summary.png".format(dirname)))
	
		if selfpredict:
			selfpredcat = megalut.learn.tenbilacrun.predict(traincat, [conf], traindir)
			megalut.tools.io.writepickle(selfpredcat, os.path.join(traindir, "{}_selfpred.pkl".format(dirname)))
			
			figpredcatpath = os.path.join(traindir, "{}_selfpred.png".format(dirname))
		
			if "s2w" in conf[0] or "g2w" in conf[0]:
				component = 2
			else:
				component = 1
	
			plot_3_validw.plot(selfpredcat, component, figpredcatpath)
			
	
