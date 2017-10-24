"""
This is to test validation set with only 4 x 2 galaxies per true shear, and error propagation

"""

import megalut.tools
import megalut.learn
import megalut

import config
import numpy as np
import os

from megalut.tools.feature import Feature
import matplotlib.pyplot as plt
import megalut.plot


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

redo = True




def main():
	
	
	sheartraindir = os.path.join(config.traindir, config.datasets["train-shear"])
	weighttraindir = os.path.join(config.traindir, config.datasets["train-weight"])

	valname = "pred_{}".format(config.datasets["valid-overall"])
	predcatpath = os.path.join(config.valdir, valname + ".pkl")

	catpath = os.path.join(config.simmeasdir, config.datasets["valid-overall"], "groupmeascat.pkl")
	
	
	if (redo is True) or (not os.path.exists(predcatpath)):
		cat = megalut.tools.io.readpickle(catpath)
		#print megalut.tools.table.info(cat)
	
		cat = megalut.learn.tenbilacrun.predict(cat, config.shearconflist , sheartraindir)
		if len(config.weightconflist) > 0:
			cat = megalut.learn.tenbilacrun.predict(cat, config.weightconflist , weighttraindir)
	
	
		megalut.tools.io.writepickle(cat, predcatpath)
	
	else:
		logger.info("Reusing existing preds")
		cat = megalut.tools.io.readpickle(predcatpath)
		#print megalut.tools.table.info(cat)
	

	
	cat["pre_s1w"] *= 40.18
	cat["pre_s1"] += -4.6e-3
	megalut.tools.table.addstats(cat, "pre_s1", "pre_s1w")
	megalut.tools.metrics.wmetrics(cat, Feature("tru_s1"), Feature("pre_s1_wmean"), wfeat=Feature("pre_s1_wmeanw"))
	
	cat["pre_s2w"] *= 30.84
	cat["pre_s2"] += -1.4e-3
	megalut.tools.table.addstats(cat, "pre_s2", "pre_s2w")
	megalut.tools.metrics.wmetrics(cat, Feature("tru_s2"), Feature("pre_s2_wmean"), wfeat=Feature("pre_s2_wmeanw"))
	
	






if __name__ == "__main__":
    main()
