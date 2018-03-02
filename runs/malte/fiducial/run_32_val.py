import matplotlib
matplotlib.use("AGG")

import megalut.tools
import megalut.learn
import megalut

import config
import numpy as np
import os

import plot_3_val_s as plot

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

	
# Getting the path to the correct directories
traindir = os.path.join(config.traindir, config.datasets["ts"])
	
# And to the validation catalogue
valcatpath = os.path.join(config.simmeasdir, config.datasets["vs"], "groupmeascat.pkl")
predcatpath = os.path.join(config.valdir, config.valname + ".pkl")


# The prediction:

cat = megalut.tools.io.readpickle(valcatpath)


select = False # prefer selecting at the plot stage, not here.

if select:
	#megalut.tools.table.addstats(cat, "snr")

	s = megalut.tools.table.Selector("fortrain", [
		#("max", "adamom_failfrac", 0.01),
		#("min", "tru_rad", 3.0),
		#("min", "snr_mean", 10.0),
	])
	cat = s.select(cat)


predcat = megalut.learn.tenbilacrun.predict(cat, config.shearconflist, traindir)

megalut.tools.io.writepickle(predcat, predcatpath)


# The quick automatic plot:
"""	
for conf in config.shearconflist: # For the plot, we go through them one by one here.
	
	# We read the file, to get a fresh one for each component:
	predcat = megalut.tools.io.readpickle(predcatpath)

	
	# And make the plot	
	if "s2" in conf[0] or "g2" in conf[0]:
		component = 2
	else:
		component = 1
	
	valfigpath = os.path.join(config.valdir, valname + "_component{}".format(component) + ".png")

	plot.plot(predcat, component, mode="s", filepath=valfigpath)
"""
