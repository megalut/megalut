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


#spname = "G3CGCSersics_train_nn"
#spname = "G3CGCSersics_train_100rea"
#spname = "G3CGCSersics_train_shear_snc100"
spname = "G3CGCSersics_train_shear_snc10000"

onlyallrea = True

conflist = [
	#("mlconfig/ada4g1.cfg", "mlconfig/sum55.cfg"),
	#("mlconfig/ada4g2.cfg", "mlconfig/sum55.cfg"),
	
	("mlconfig/ada4s1.cfg", "mlconfig/sum55.cfg"),
	
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
	
	if onlyallrea:
		cat["adanbad"] = np.sum(cat["adamom_g1"].mask, axis=1)
		s = megalut.tools.table.Selector("allrea", [
			#("is", "adanbad", 0),
			("max", "adanbad", 50),
		])
		cat = s.select(cat)
	
	#exit()	
	#print megalut.tools.table.info(cat)
				
	# Running the training
	dirnames = megalut.learn.tenbilacrun.train(cat, conflist, traindir)
	
	# And saving a summary plot next to the tenbilac working directories
	for dirname in dirnames:
		tenbilacdirpath = os.path.join(traindir, dirname)
		ten = tenbilac.com.Tenbilac(tenbilacdirpath)
		ten._readmembers()
		tenbilac.plot.summaryerrevo(ten.committee, filepath=os.path.join(traindir, "{}_summary.png".format(dirname)))

	# Self-predicting
