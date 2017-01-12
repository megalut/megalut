import matplotlib
matplotlib.use("AGG")


import megalut
import config
import measfcts
import simparams
import mlparams

import glob
import os
import numpy as np
import astropy

import logging
logger = logging.getLogger(__name__)



traindir = os.path.join(config.workdir, "train_Nico4nn_2feat-multreallyfix55")



# Training
catpath = os.path.join(config.simdir, "Nico4nn", "groupmeascat.pkl")

cat = megalut.tools.io.readpickle(catpath)
#print megalut.tools.table.info(cat)
megalut.learn.run.train(cat, traindir, mlparams.trainparamslist)


# Self-predicting

precatpath = os.path.join(traindir, "selfprecat.pkl")

cat = megalut.tools.io.readpickle(catpath)
cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
megalut.tools.io.writepickle(cat, precatpath)




# Predicting the validation set

valcatpath = os.path.join(config.simdir, "Nico4shear", "groupmeascat_cases.pkl")
valprecatpath = os.path.join(traindir, "valprecat.pkl")

cat = megalut.tools.io.readpickle(valcatpath)
cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
megalut.tools.io.writepickle(cat, valprecatpath)




