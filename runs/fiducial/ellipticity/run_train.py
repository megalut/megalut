import matplotlib
matplotlib.use("AGG")

import os

import megalut.learn

import includes

import logging
logger = logging.getLogger(__name__)



traindir = os.path.join(includes.workdir, "train_simple")

conflist = [
	("config/ada3g1.cfg", "config/Net.cfg"),
]


# Training
catpath = os.path.join(includes.simdir, "Ellipticity", "groupmeascat.pkl")

cat = megalut.tools.io.readpickle(catpath)
#print megalut.tools.table.info(cat)
megalut.learn.tenbilacrun.train(cat, conflist, traindir)

#megalut.learn.run.train(cat, traindir, mlparams.trainparamslist)


# Self-predicting

precatpath = os.path.join(traindir, "selfprecat.pkl")

cat = megalut.tools.io.readpickle(catpath)
#cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
cat = megalut.learn.tenbilacrun.predict(cat, conflist, traindir)
megalut.tools.io.writepickle(cat, precatpath)



