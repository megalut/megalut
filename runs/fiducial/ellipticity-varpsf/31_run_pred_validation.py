import matplotlib
matplotlib.use("AGG")

import os

import megalut.learn

import includes

import logging
logger = logging.getLogger(__name__)



traindir = os.path.join(includes.workdir, "train_simple")

conflist = [
	("config/ada5g1.cfg", "config/Net.cfg"),
	("config/ada5g2.cfg", "config/Net.cfg"),
]



# Predicting the validation set

valcatpath = os.path.join(includes.simvaldir, "EllipticityVarPSF", "groupmeascat_cases.pkl")
valprecatpath = os.path.join(traindir, "valprecat.pkl")

cat = megalut.tools.io.readpickle(valcatpath)
#cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
cat = megalut.learn.tenbilacrun.predict(cat, conflist, traindir)
megalut.tools.io.writepickle(cat, valprecatpath)



