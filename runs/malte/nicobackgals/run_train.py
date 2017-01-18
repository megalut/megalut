import matplotlib
matplotlib.use("AGG")


import megalut
import config
import measfcts
import simparams
import mlparams

import glob
import os
import numpy as np
import astropy

import logging
logger = logging.getLogger(__name__)



#traindir = os.path.join(config.workdir, "train_Nico4nn_2feat-multreallyfix55")
#traindir = os.path.join(config.workdir, "train_Nico4nn_Sum55")
#traindir = os.path.join(config.workdir, "train_Nico4nn_3feat-sum55")
#traindir = os.path.join(config.workdir, "train_Nico4nn_3feat-free3m33")
#traindir = os.path.join(config.workdir, "train_Nico4nn_2feat-sum55")
#traindir = os.path.join(config.workdir, "train_Nico4nn_3feat-sum55_norm-11")
#traindir = os.path.join(config.workdir, "train_Nico4nn_3featfou-sum55")
#traindir = os.path.join(config.workdir, "train_Nico4nn_3featg1g2-sum55")
#traindir = os.path.join(config.workdir, "train_Nico4nn_sum55")


#traindir = os.path.join(config.workdir, "train_Nico4nn_g1ada5_sum55")
traindir = os.path.join(config.workdir, "train_Nico4nn_g1ada5_mult55free")
#traindir = os.path.join(config.workdir, "train_Nico4nn_g1ada5_sum55really5")


# Training
catpath = os.path.join(config.simdir, "Nico4nn", "groupmeascat.pkl")


cat = megalut.tools.io.readpickle(catpath)
#print megalut.tools.table.info(cat)
#exit()
megalut.learn.run.train(cat, traindir, mlparams.trainparamslist)


# Self-predicting

precatpath = os.path.join(traindir, "selfprecat.pkl")

cat = megalut.tools.io.readpickle(catpath)
cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)
megalut.tools.io.writepickle(cat, precatpath)



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

