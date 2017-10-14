import matplotlib
matplotlib.use("AGG")

import os

import megalut.learn

import config

import logging
logger = logging.getLogger(__name__)



traindir = os.path.join(config.workdir, "train_default")

conflist = [
	("config/ada2s1w.cfg", "config/sum3w_1.cfg"),
	("config/ada2s2w.cfg", "config/sum3w_1.cfg"),
]

# Training
catpath = os.path.join(traindir, "groupmeascat_cases_prew.pkl")

cat = megalut.tools.io.readpickle(catpath)

print megalut.tools.table.info(cat)

s = megalut.tools.table.Selector("ok", [
	#("in", "snr_mean", 5, 150),
	#("in", "tru_rad", 0, 11),
	("max", "adamom_sigma", 4.7)
	]
	)

#cat = s.select(cat)

print megalut.tools.table.info(cat)
megalut.learn.tenbilacrun.train(cat, conflist, traindir)

#megalut.learn.run.train(cat, traindir, mlparams.trainparamslist)


# Self-predicting

precatpath = os.path.join(traindir, "groupmeascat_cases_pred_wpred.pkl")

cat = megalut.tools.io.readpickle(catpath)
#cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
cat = megalut.learn.tenbilacrun.predict(cat, conflist, traindir)
megalut.tools.io.writepickle(cat, precatpath)


