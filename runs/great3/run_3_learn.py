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


spname = "G3CGCSersics_train_nn"

conflist = [
	("mlconfig/ada4g1.cfg", "mlconfig/sum55.cfg"),
	("mlconfig/ada4g2.cfg", "mlconfig/sum55.cfg"),
]


for subfield in config.great3.subfields:
	
	
	logger.info("Working on subfield {}".format(subfield))
	
	# Getting the path to the correct directories
	measdir = config.great3.path("simmeas","%03i" % subfield)
	traindir = config.great3.path("ml", "%03i" % subfield)
	
	# And to the catalogue
	traincatpath = os.path.join(measdir, spname, "groupmeascat.pkl")
	traincat = megalut.tools.io.readpickle(traincatpath)

	# Preparing tenbilac logging:
	#if not os.path.isdir(traindir):
	#	os.makedirs(traindir)
	#fh = logging.FileHandler(os.path.join(traindir, "log.txt"))
	#fh.setLevel(logging.DEBUG)
	
	
	# Running the training
	#tbllogger.addHandler(fh)
	#tbllogger.propagate = False
	
	dirnames = megalut.learn.tenbilacrun.train(traincat, conflist, traindir)
	
	#tbllogger.removeHandler(fh)
	#tbllogger.propagate = True
	
	
	# And saving a summary plot next to the tenbilac working directories
	for dirname in dirnames:
		tenbilacdirpath = os.path.join(traindir, dirname)
		ten = tenbilac.com.Tenbilac(tenbilacdirpath)
		ten._readmembers()
		tenbilac.plot.summaryerrevo(ten.committee, filepath=os.path.join(traindir, "{}_summary.png".format(dirname)))





# Remembering the name of the trainparams:
#great3.trainparams_name = trainname
#great3.trainparamslist = mymlparams.trainparams['list'] 
#great3.save_config()
