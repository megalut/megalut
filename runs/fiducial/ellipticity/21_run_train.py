import matplotlib
matplotlib.use("AGG")

import os

import megalut.learn

import includes
import numpy as np

import logging
logger = logging.getLogger(__name__)



traindir = os.path.join(includes.workdir, "train_noisy")

conflist = [
	("config/ada3g1.cfg", "config/Net.cfg"),
	("config/ada3g2.cfg", "config/Net.cfg"),
]


# Training
catpath = os.path.join(includes.simdir, "Ellipticity", "groupmeascat_cases.pkl")

cat = megalut.tools.io.readpickle(catpath)

cat["adamom_frac"] = np.sum(cat["adamom_g1"].mask, axis=1)/float(cat["adamom_g1"].shape[1])

# Only making sure there's no (too) bad examples in the training set
s = megalut.tools.table.Selector("ok", [
	("max", "adamom_frac", 0.005)
	]
	)

cat = s.select(cat)

megalut.learn.tenbilacrun.train(cat, conflist, traindir)


# Self-predicting

precatpath = os.path.join(traindir, "selfprecat.pkl")

cat = megalut.tools.io.readpickle(catpath)
#cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
cat = megalut.learn.tenbilacrun.predict(cat, conflist, traindir)
megalut.tools.io.writepickle(cat, precatpath)



