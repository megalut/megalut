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



import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)



def main():

	
	catpath = os.path.join(config.simmeasdir, config.datasets["train-weight"], "groupmeascat_predforw.pkl")
	cat = megalut.tools.io.readpickle(catpath)

	weighttraindir = os.path.join(config.traindir, config.datasets["train-weight"])
	
	# Running the training	
	dirnames = megalut.learn.tenbilacrun.train(cat, config.weightconflist, weighttraindir)
				

if __name__ == "__main__":
    main()
