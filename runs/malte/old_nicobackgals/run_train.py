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
traincatpath = os.path.join(config.simdir, "Nico4nn", "groupmeascat.pkl")

#traindir = os.path.join(config.workdir, "train_Nico4")
#traincatpath = os.path.join(config.simdir, "Nico4", "groupmeascat.pkl")


conflist = [
	("conf/ada4g1.cfg", "conf/sum55.cfg")
	#("conf/ada4g2.cfg", "conf/sum55.cfg")
	#("conf/ada4g1.cfg", "conf/sum55.cfg")
	#("conf/ada4g2.cfg", "conf/sum55.cfg")
	#("conf/ada4g1.cfg", "conf/mult44free.cfg")
	#("conf/fh4g1.cfg", "conf/sum55.cfg")
	#("conf/fh4g2.cfg", "conf/sum55.cfg")
	#("conf/fh4g1.cfg", "conf/sum55mbf1.cfg")
	#("conf/fh4g2.cfg", "conf/sum55mbf1.cfg") # dit not run, look g1 first
	#("conf/fh4g1.cfg", "conf/sum55_pretrained.cfg")
	#("conf/ada4g1.cfg", "conf/mult33free.cfg")
	#("conf/ada4g1.cfg", "conf/mult22fmb.cfg")
	#("conf/ada4g1.cfg", "conf/minimult21.cfg")
]



traincat = megalut.tools.io.readpickle(traincatpath)
dirnames = megalut.learn.tenbilacrun.train(traincat, conflist, traindir)
dirname = dirnames[0]

#dirname = "fh4g1_sum55"
#dirname = "ada4g1_mult22fmb"


# Self-predicting

precatpath = os.path.join(traindir, dirname, "selfprecat.pkl")

cat = megalut.tools.io.readpickle(traincatpath)
cat = megalut.learn.tenbilacrun.predict(cat, conflist, traindir)
print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, precatpath)


# Predicting the validation set

valcatpath = os.path.join(config.simdir, "Nico4shear_snc10000", "groupmeascat_cases.pkl")
valprecatpath = os.path.join(traindir, dirname, "valprecat.pkl")

cat = megalut.tools.io.readpickle(valcatpath)
cat = megalut.learn.tenbilacrun.predict(cat, conflist, traindir)
megalut.tools.io.writepickle(cat, valprecatpath)


# Idem for the low-SN set:

valcatpath = os.path.join(config.simdir, "Nico4shear_snc10000_lowSN", "groupmeascat_cases.pkl")
valprecatpath = os.path.join(traindir, dirname, "valprecat_lowSN.pkl")

cat = megalut.tools.io.readpickle(valcatpath)
cat = megalut.learn.tenbilacrun.predict(cat, conflist, traindir)
megalut.tools.io.writepickle(cat, valprecatpath)


