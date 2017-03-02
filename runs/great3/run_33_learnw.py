import matplotlib
matplotlib.use("AGG")


import megalut.tools
import megalut.learn
import megalut
import tenbilac

import config
import numpy as np
import os


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)
#tbllogger = logging.getLogger("tenbilac")


spname = "G3CGCSersics_statshear"

conflist = [
	("mlconfig/ada2s1w.cfg", "mlconfig/sum3w.cfg")
]

selfpredict = True


for subfield in config.great3.subfields:
	
	
	logger.info("Working on subfield {}".format(subfield))
	
	# Getting the path to the correct directories
	measdir = config.great3.path("simmeas","%03i" % subfield)
	traindir = config.great3.path("ml", "%03i" % subfield)
	
	# And to the catalogue
	traincatpath = os.path.join(measdir, spname, "groupmeascat_cases_pred.pkl")
	traincat = megalut.tools.io.readpickle(traincatpath)
	
	# Running the training	
	dirnames = megalut.learn.tenbilacrun.train(traincat, conflist, traindir)
		
	# And saving a summary plot next to the tenbilac working directories
	for dirname in dirnames:
		tenbilacdirpath = os.path.join(traindir, dirname)
		ten = tenbilac.com.Tenbilac(tenbilacdirpath)
		ten._readmembers()
		tenbilac.plot.summaryerrevo(ten.committee, filepath=os.path.join(traindir, "{}_summary.png".format(dirname)))
	
	if selfpredict:
		selfpredcat = megalut.learn.tenbilacrun.predict(traincat, conflist, traindir)
		megalut.tools.io.writepickle(selfpredcat, os.path.join(measdir, spname, "groupmeascat_cases_pred_wpred.pkl"))
	
