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

mode = "s"
#mode = "w"
netid = 0 # id of the network to show


if mode is "s":
	workbasedir = os.path.join(config.traindir, config.datasets["ts"])
	conflist = config.shearconflist
elif mode is "w":
	workbasedir = os.path.join(config.traindir, "{}_with_{}".format(config.datasets["tw"], config.datasets["ts"]))
	conflist = config.weightconflist



for (dataconfpath, toolconfpath) in conflist:

	toolconfig = megalut.learn.tenbilacrun.readconfig(toolconfpath)
	dataconfig = megalut.learn.tenbilacrun.readconfig(dataconfpath)
	confname = dataconfig.get("setup", "name") + "_" + toolconfig.get("setup", "name")
	trainworkdir = os.path.join(workbasedir, confname) # We will pass this to Tenbilac
	
	
	tblconfiglist = [("setup", "workdir", trainworkdir)]
	ten = tenbilac.com.Tenbilac(toolconfpath, tblconfiglist)
       
	ten._readmembers()
	
	
	net = ten.committee[netid].net
	
	#fig = plt.figure(figsize=(6, 6))
	#ax = fig.add_subplot(1, 1, 1)

	if mode is "s":
		net.onames[0] = r"\hat{g}"+net.onames[0][-1]
		filepath = os.path.join(config.valdir, config.datasets["ts"] + "_" + confname + "_netviz.pdf")
	elif mode is "w":
		net.onames[0] = r"\hat{w}"+net.onames[0][-1]
		filepath = os.path.join(config.valdir,  "{}_with_{}".format(config.datasets["tw"], config.datasets["ts"]) + "_" + confname + "_netviz.pdf")
	
	tenbilac.plot.netviz(ten.committee[netid].net, filepath=filepath)       
	
	

	#megalut.plot.figures.savefig(os.path.join(config.valdir, config.datasets["ts"] + "_" + confname + "_msbevo"), fig, fancy=True, pdf_transparence=True)
	#plt.show()
