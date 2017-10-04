import matplotlib
matplotlib.use("AGG")

import os

import megalut.learn
import megalut.tools

import config

import logging
logger = logging.getLogger(__name__)



traindir = os.path.join(config.workdir, "train_simple")

conflist = [
	("config/ada3g1.cfg", "config/Net_99.cfg"),
	("config/ada3g2.cfg", "config/Net_99.cfg"),
]



# Predicting the validation set

valcatpath = os.path.join(config.simvaldir, "EuclidLike_Ell", "groupmeascat_cases.pkl")
valprecatpath = os.path.join(traindir, "valprecat.pkl")

cat = megalut.tools.io.readpickle(valcatpath)
print megalut.tools.table.info(cat)
#cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
cat = megalut.learn.tenbilacrun.predict(cat, conflist, traindir)
megalut.tools.io.writepickle(cat, valprecatpath)



