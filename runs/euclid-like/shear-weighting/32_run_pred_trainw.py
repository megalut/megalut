import matplotlib
matplotlib.use("AGG")

import os

import megalut.learn
import megalut.tools as tls

import config

import logging
logger = logging.getLogger(__name__)



traindir = os.path.join(config.workdir, "train_simple")

conflist = [
	("config/ada3s1.cfg", "config/Net.cfg"),
	("config/ada3s2.cfg", "config/Net.cfg"),
]



# Predicting the validation set
spname = "EuclidLike_statshear"
valcatpath = os.path.join(config.simwdir, spname, "groupmeascat_cases.pkl")
valprecatpath = os.path.join(traindir, "groupmeascat_cases_prew.pkl")

cat = megalut.tools.io.readpickle(valcatpath)


#cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
cat = megalut.learn.tenbilacrun.predict(cat, conflist, traindir)

print tls.table.info(cat)
megalut.tools.io.writepickle(cat, valprecatpath)


