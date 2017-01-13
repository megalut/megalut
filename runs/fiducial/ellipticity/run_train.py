import matplotlib
matplotlib.use("AGG")

import mlparams
import os

import megalut.learn

import includes

import logging
logger = logging.getLogger(__name__)



traindir = os.path.join(includes.workdir, "train_simple")


# Training
catpath = os.path.join(includes.simdir, "Ellipticity", "groupmeascat.pkl")

cat = megalut.tools.io.readpickle(catpath)
#print megalut.tools.table.info(cat)
megalut.learn.run.train(cat, traindir, mlparams.trainparamslist)


# Self-predicting

precatpath = os.path.join(traindir, "selfprecat.pkl")

cat = megalut.tools.io.readpickle(catpath)
cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
megalut.tools.io.writepickle(cat, precatpath)



