import matplotlib
matplotlib.use("AGG")

import os

import megalut.learn

import config
import numpy as np
import logging
logger = logging.getLogger(__name__)



traindir = os.path.join(config.workdir, "train_nonoise4")

conflist = [
	#("config/ada4s1.cfg", "config/Net.cfg"),
	("config/ada4s2.cfg", "config/Net.cfg"),
]


# Training
catpath = os.path.join(config.workdir, "sim", "EuclidLike_Ell", "groupmeascat_cases.pkl")

cat = megalut.tools.io.readpickle(catpath)


cat["adamom_frac"] = np.sum(cat["adamom_g1"].mask, axis=1)/float(cat["adamom_g1"].shape[1])
megalut.tools.table.addstats(cat, "snr")
s = megalut.tools.table.Selector("ok", [
	("min", "snr_mean", 10),
	("max", "adamom_frac", 0.005)
	]
	)

cat = s.select(cat)


print megalut.tools.table.info(cat)

megalut.learn.tenbilacrun.train(cat, conflist, traindir)

# Self-predicting

precatpath = os.path.join(traindir, "selfprecat.pkl")

cat = megalut.tools.io.readpickle(catpath)
#cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
cat = megalut.learn.tenbilacrun.predict(cat, conflist, traindir)
megalut.tools.io.writepickle(cat, precatpath)



