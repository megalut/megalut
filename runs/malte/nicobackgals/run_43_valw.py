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


# Load validation catalog

catpath = os.path.join(config.simmeasdir, config.datasets["vo"], "groupmeascat.pkl")
cat = megalut.tools.io.readpickle(catpath)

# Predict point estimates:

traindir = os.path.join(config.traindir, config.datasets["tp"])
predcat = megalut.learn.tenbilacrun.predict(cat, config.shearconflist, traindir)


# Predict weights:
if len(config.weightconflist) > 0:
	wtraindir = os.path.join(config.traindir, config.datasets["tw"] + "_with_" + config.datasets["tp"] + "_" + config.sconfname)
	predcat = megalut.learn.tenbilacrun.predict(predcat, config.weightconflist, wtraindir)
	predcatpath = os.path.join(config.valdir, config.wvalname+".pkl")

else:
	predcatpath = os.path.join(config.valdir, config.valname+".pkl")


# Save the prediction:
megalut.tools.io.writepickle(predcat, predcatpath)


