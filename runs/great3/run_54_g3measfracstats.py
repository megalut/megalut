#import matplotlib
#matplotlib.use("AGG")

import matplotlib.pyplot as plt

import megalut
import megalut.tools
import megalutgreat3
import astropy


import config
import numpy as np
import os


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)


subfields = []
psfsigmas = []
nfails = []


for subfield in config.great3.subfields:
	
	predcatpath = config.great3.subpath(subfield, "pred", "predcat_{}.pkl".format(config.predcode))
	cat = megalut.tools.io.readpickle(predcatpath)
	
	#print megalut.tools.table.info(cat)
	#n = float(len(cat))
	#print subfield, np.sum(cat["pre_s1"].mask), np.sum(cat["adamom_g1"].mask)
	
	subfields.append(subfield)
	nfails.append(np.sum(cat["pre_s1"].mask))
	psfsigmas.append(np.mean(cat["psf_adamom_sigma"]))
	
	
plt.scatter(psfsigmas, nfails)
plt.show()
