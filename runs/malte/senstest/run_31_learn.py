import matplotlib
matplotlib.use("AGG")


import megalut.tools
import megalut.learn
import megalut
import tenbilac

import config
import numpy as np
import os

#from megalut.tools.feature import Feature
#import matplotlib.pyplot as plt


import logging
#logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

select = True

	
# Getting the path to the correct directories
measdir = os.path.join(config.simmeasdir, config.datasets["train-shear"])
traindir = os.path.join(config.traindir, config.datasets["train-shear"])
	
# And to the catalogue
traincatpath = os.path.join(measdir, "groupmeascat.pkl")
cat = megalut.tools.io.readpickle(traincatpath)
#print megalut.tools.table.info(cat)

nrea = cat["adamom_g1"].shape[1]
logger.info("We have {} realizations".format(nrea))
cat["adamom_failfrac"] = np.sum(cat["adamom_g1"].mask, axis=1) / float(nrea)


select = True	
if select:
	s = megalut.tools.table.Selector("fortrain", [
		("max", "adamom_failfrac", 0.1),
	])
	cat = s.select(cat)
	
#exit()	
#print megalut.tools.table.info(cat)
	
	
# Running the training
dirnames = megalut.learn.tenbilacrun.train(cat, config.shearconflist, traindir)

"""	
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
	
"""
