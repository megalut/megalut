import matplotlib
matplotlib.use("AGG")


import megalut
import config
import measfcts
import simparams

import glob
import os
import numpy as np
import astropy

import logging
logger = logging.getLogger(__name__)




traindir = os.path.join(config.workdir, "train_Nico4nn")
catpath = os.path.join(config.simdir, "Nico4nn", "groupmeascat.pkl")

cat = megalut.tools.io.readpickle(catpath)

conflist = [
	#("conf/ada4g1.cfg", "conf/sum55.cfg"),
	#("conf/ada4g2.cfg", "conf/sum55.cfg")
	("conf/ada4g1.cfg", "conf/sum55.cfg")
	#("conf/ada4g1.cfg", "conf/mult44free.cfg")
]


dirnames = megalut.learn.tenbilacrun.train(cat, conflist, traindir)

exit()

# Self-predicting
precatpath = os.path.join(traindir, dirnames[0], "selfprecat.pkl")

#cat = megalut.tools.io.readpickle(catpath)
cat = megalut.learn.tenbilacrun.predict(cat, conflist, traindir)

print megalut.tools.table.info(cat)

megalut.tools.io.writepickle(cat, precatpath)




exit()

# Predicting the validation set

valcatpath = os.path.join(config.simdir, "Nico4shear_snc10000", "groupmeascat_cases.pkl")
valprecatpath = os.path.join(traindir, "valprecat.pkl")
#valcatpath = os.path.join(config.simdir, "Nico4shear", "groupmeascat_cases.pkl")
#valprecatpath = os.path.join(traindir, "valprecat.pkl")


cat = megalut.tools.io.readpickle(valcatpath)
cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
megalut.tools.io.writepickle(cat, valprecatpath)

# Idem for the low-SN set:

valcatpath = os.path.join(config.simdir, "Nico4shear_snc10000_lowSN", "groupmeascat_cases.pkl")
valprecatpath = os.path.join(traindir, "valprecat_lowSN.pkl")

cat = megalut.tools.io.readpickle(valcatpath)
cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
megalut.tools.io.writepickle(cat, valprecatpath)

