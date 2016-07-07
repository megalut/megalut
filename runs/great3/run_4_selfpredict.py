import os

import megalut.tools as tools
import megalut.learn as learn

import config

import megalutgreat3 as mg3
import plots

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)

#TODO: This should run on the training data AND validation set!!!

# Loading the correct configuration!
great3 = mg3.great3.load_config(outdir='cgc')

# The training used by default in training is the one defined in:
# great3.trainparams_name
trainname = great3.trainparams_name
trainparamslist = great3.trainparamslist

# The simulation used by default in training is the one defined in:
# great3.simparams_name
simparams_name = great3.simparams_name

for subfield in great3.subfields:
	
	# Getting the path to the correct directories
	simdir = great3.get_path("sim","%03i" % subfield)
	measdir = great3.get_path("simmeas", "%03i" % subfield)
	traindir = great3.get_path("ml", "%03i" % subfield, trainname, simparams_name)
	
	# Loading the training data
	cat = tools.io.readpickle(os.path.join(measdir, simparams_name, "groupmeascat.pkl"))
	
	# Predicting the training data
	cat = learn.run.predict(cat, traindir, trainparamslist)
	tools.io.writepickle(cat, os.path.join(traindir, "predtraincat.pkl"))
	
plots.show_selfpredict_shear(great3, trainname=trainname, simname=simparams_name, outdir=great3.get_path("pred"), show=False)
