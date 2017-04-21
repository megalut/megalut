import matplotlib
matplotlib.use("AGG")

import megalut.tools
import megalut.learn
import megalut

import config
import numpy as np
import os


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main():

	catpath = os.path.join(config.simmeasdir, config.datasets["train-weight"], "groupmeascat.pkl")
	cat = megalut.tools.io.readpickle(catpath)
	
	sheartraindir = os.path.join(config.traindir, config.datasets["train-shear"])
	cat = megalut.learn.tenbilacrun.predict(cat, config.shearconflist , sheartraindir)

	#print megalut.tools.table.info(cat)
	#exit()

	predcatpath = os.path.join(config.simmeasdir, config.datasets["train-weight"], "groupmeascat_predforw.pkl")
	megalut.tools.io.writepickle(cat, predcatpath)
	
	


if __name__ == "__main__":
    main()
