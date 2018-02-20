import config
import measfcts
import os
import numpy as np
import matplotlib.ticker as ticker
import matplotlib

import tenbilac
import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)


megalut.plot.figures.set_fancy(14)

workbasedir = os.path.join(config.traindir, config.datasets["ts"])


for (dataconfpath, toolconfpath) in config.shearconflist:

	toolconfig = megalut.learn.tenbilacrun.readconfig(toolconfpath)
	dataconfig = megalut.learn.tenbilacrun.readconfig(dataconfpath)
	confname = dataconfig.get("setup", "name") + "_" + toolconfig.get("setup", "name")
	trainworkdir = os.path.join(workbasedir, confname) # We will pass this to Tenbilac
	
	
	tblconfiglist = [("setup", "workdir", trainworkdir)]
	ten = tenbilac.com.Tenbilac(toolconfpath, tblconfiglist)
       
	ten._readmembers()
	
	netid = 5
	
	net = ten.committee[netid].net
	net.onames[0] = r"\hat{g}"+net.onames[0][-1]
	
	#fig = plt.figure(figsize=(6, 6))
	#ax = fig.add_subplot(1, 1, 1)

	filepath = os.path.join(config.valdir, config.datasets["ts"] + "_" + confname + "_netviz.pdf")
	
	tenbilac.plot.netviz(ten.committee[netid].net, filepath=filepath)       
	
	

	#megalut.plot.figures.savefig(os.path.join(config.valdir, config.datasets["ts"] + "_" + confname + "_msbevo"), fig, fancy=True, pdf_transparence=True)
	#plt.show()
