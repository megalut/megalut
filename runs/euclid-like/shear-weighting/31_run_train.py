import matplotlib
matplotlib.use("AGG")

import os

import megalut.learn

import config

import logging
logger = logging.getLogger(__name__)



traindir = os.path.join(config.workdir, "train_simple")

conflist = [
	("config/ada3s1.cfg", "config/Net.cfg"),
	("config/ada3s2.cfg", "config/Net.cfg"),
]


# Training
catpath = os.path.join(config.simdir, "EuclidLike_Ell", "groupmeascat.pkl")

cat = megalut.tools.io.readpickle(catpath)
megalut.learn.tenbilacrun.train(cat, conflist, traindir)

# Self-predicting

precatpath = os.path.join(traindir, "selfprecat.pkl")

cat = megalut.tools.io.readpickle(catpath)
#cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
cat = megalut.learn.tenbilacrun.predict(cat, conflist, traindir)
megalut.tools.io.writepickle(cat, precatpath)



