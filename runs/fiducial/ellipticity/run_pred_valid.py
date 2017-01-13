import matplotlib
matplotlib.use("AGG")

import mlparams
import os

import megalut.learn

import includes

import logging
logger = logging.getLogger(__name__)



traindir = os.path.join(includes.workdir, "train_simple")



# Predicting the validation set

valcatpath = os.path.join(includes.simvaldir, "Ellipticity", "groupmeascat_cases.pkl")
valprecatpath = os.path.join(traindir, "valprecat.pkl")

cat = megalut.tools.io.readpickle(valcatpath)
cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
megalut.tools.io.writepickle(cat, valprecatpath)



