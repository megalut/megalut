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




catpath = os.path.join(config.simmeasdir, config.datasets["tw"], "groupmeascat.pkl")
cat = megalut.tools.io.readpickle(catpath)

#print megalut.tools.table.info(cat)
#exit()

predcatpath = os.path.join(config.simmeasdir, config.datasets["tw"], "groupmeascat_predforw.pkl")



traindir = os.path.join(config.traindir, config.datasets["ts"])
	
predcat = megalut.learn.tenbilacrun.predict(cat, config.shearconflist, traindir)

megalut.tools.io.writepickle(predcat, predcatpath)
	
	
