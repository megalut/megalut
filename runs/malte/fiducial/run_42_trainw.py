import matplotlib
matplotlib.use("AGG")

import argparse

import megalut.tools
import megalut.learn
import megalut
import tenbilac

import config
import numpy as np
import os
import glob
import shutil

#import plot_3_valw


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)



wtraindir = os.path.join(config.traindir, config.datasets["tw"] + "_with_" + config.datasets["ts"])
catpath = os.path.join(wtraindir, "groupmeascat_predforw.pkl")

cat = megalut.tools.io.readpickle(catpath)

		
"""
# Now we might want to copy an existing training to start from there.
if args.startfrom is not None:
	logger.info("Copying existing training from {}...".format(args.startfrom))

	dirnames = megalut.learn.tenbilacrun.confnames(config.weightconflist)
	for (dirname, conf) in zip(dirnames, config.weightconflist):
		newtraindirpath = os.path.join(traindir, dirname)
		if os.path.isdir(newtraindirpath):
			raise RuntimeError("A training already exists, but you want me to start from another one")
		
		#pretrainminipaths = sorted(glob.glob(config.great3.subpath(args.startfrom, "ml", config.datasets["train-weight"], dirname, "mini_*")))
		#if len(pretrainminipaths) == 0:
		#	raise RuntimeError("Could not find pre-training!")
		#pretrainpath = pretrainminipaths[-1] # Taking the last one
		
		# Let's not take mini, but the full one
		pretrainpath = config.great3.subpath(args.startfrom, "ml", config.datasets["train-weight"], dirname)
		logger.info("Copying {} into {}...".format(pretrainpath, newtraindirpath))
		shutil.copytree(pretrainpath, newtraindirpath)
		print "##############################   Is it ok to keep the normer ?"
"""

	
# Running the training	
dirnames = megalut.learn.tenbilacrun.train(cat, config.weightconflist, wtraindir)

print dirnames

#dirnames = ["ada4s1w_sum33wmassshort", "ada4s2w_sum33wmassshort"]

"""
# Summary plot and self-predictions
for dirname in dirnames:
	tenbilacdirpath = os.path.join(traindir, dirname)
	ten = tenbilac.com.Tenbilac(tenbilacdirpath)
	ten._readmembers()
	tenbilac.plot.summaryerrevo(ten.committee, filepath=os.path.join(traindir, "{}_summary.png".format(dirname)))


	cat = megalut.tools.io.readpickle(catpath) # To get the full catalog with all cases	
	
	for (dirname, conf) in zip(dirnames, config.weightconflist):

		predcat = megalut.learn.tenbilacrun.predict(cat, [conf], traindir)
		predcatpath = os.path.join(traindir, "{}_selfpred.pkl".format(dirname))
		megalut.tools.io.writepickle(predcat, predcatpath)
		figpredcatpath = os.path.join(traindir, "{}_selfpred.png".format(dirname))
		
		if "s2" in conf[0] or "g2" in conf[0]:
			component = 2
		else:
			component = 1
		plot_3_valw.plot(predcat, component, filepath=figpredcatpath)
			
"""
