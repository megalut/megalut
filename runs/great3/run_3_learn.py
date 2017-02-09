import megalut.tools
import megalut.learn
import megalut

import config
import numpy as np
import os


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Loading the run
great3 = config.load_run()

spname = "G3CGCSersics_train_nn"

conflist = [
	("mlconfig/ada4g1.cfg", "mlconfig/sum55.cfg")
]


for subfield in config.subfields:
	
	
	logger.info("Working on subfield {}".format(subfield))
	
	# Getting the path to the correct directories
	measdir = great3.path("simmeas","%03i" % subfield)
	traindir = great3.path("ml", "%03i" % subfield)
	
	
	traincatpath = os.path.join(measdir, spname, "groupmeascat.pkl")
	traincat = megalut.tools.io.readpickle(traincatpath)

	
	dirnames = megalut.learn.tenbilacrun.train(traincat, conflist, traindir)
	
	print dirnames
	#dirname = dirnames[0]



# Remembering the name of the trainparams:
#great3.trainparams_name = trainname
#great3.trainparamslist = mymlparams.trainparams['list'] 
#great3.save_config()
