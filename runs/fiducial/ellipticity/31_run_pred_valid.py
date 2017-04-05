import matplotlib
matplotlib.use("AGG")

import os

import megalut.learn
import megalut.tools

import includes

import logging
logger = logging.getLogger(__name__)



traindir = os.path.join(includes.workdir, "train_simple")

conflist = [
	("config/ada3g1.cfg", "config/Net.cfg"),
	("config/ada3g2.cfg", "config/Net.cfg"),
]



# Predicting the validation set

valcatpath = os.path.join(includes.simvaldir, "Ellipticity", "groupmeascat_cases.pkl")
valprecatpath = os.path.join(traindir, "valprecat.pkl")

cat = megalut.tools.io.readpickle(valcatpath)
print megalut.tools.table.info(cat)
#cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
cat = megalut.learn.tenbilacrun.predict(cat, conflist, traindir)
megalut.tools.io.writepickle(cat, valprecatpath)



