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

# Build a name to save the overall validation: 
sconfname = os.path.splitext(os.path.basename(config.shearconflist[0][1]))[0] # extracts e.g. "sum55"
wconfname = os.path.splitext(os.path.basename(config.weightconflist[0][1]))[0] # extracts e.g. "sum55w"
valname = "{}_and_{}_with_{}_{}_on_{}".format(config.datasets["ts"], config.datasets["tw"], sconfname, wconfname, config.datasets["vo"])



# Load validation catalog

catpath = os.path.join(config.simmeasdir, config.datasets["vo"], "groupmeascat.pkl")
cat = megalut.tools.io.readpickle(catpath)

# Predict point estimates:

traindir = os.path.join(config.traindir, config.datasets["ts"])
predcat = megalut.learn.tenbilacrun.predict(cat, config.shearconflist, traindir)


# Predict weights:

traindir = os.path.join(config.traindir, config.datasets["tw"])
predcat = megalut.learn.tenbilacrun.predict(predcat, config.weightconflist, traindir)


# Save the prediction:

predcatpath = os.path.join(config.valdir, valname+".pkl")
megalut.tools.io.writepickle(predcat, predcatpath)


