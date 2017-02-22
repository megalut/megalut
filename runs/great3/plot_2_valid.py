"""
Validation plot
"""

import megalut
import megalutgreat3
import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt
import numpy as np

import config

import os
import logging
logging.basicConfig(format=config.loggerformat, level=logging.INFO)
logger = logging.getLogger(__name__)



predname = "ada4_sum55_valid"
component = 1 # which shear component


def main():


	for subfield in config.great3.subfields:
		
		predcatpath = config.great3.path("ml", "%03i" % subfield, "predcat_{}.pkl".format(predname))
		cat = megalut.tools.io.readpickle(predcatpath)
		print megalut.tools.table.info(cat)


		#bestsub = megalut.tools.table.Selector("bestsub", [("is", "subfield", subfield)])
		#simcat = bestsub.select(simcat)
		#print megalut.tools.table.info(simcat)

	
		plotpath = None
		#plotpath = config.great3.path("ml","%03i" % subfield, "valplot_{}_comp{}.png".format(predname, component))
		
		plot(cat, component, filepath=plotpath)
		logger.info("Plotted to {}".format(plotpath))




def plot(cat, component, filepath=None):

	#cat["adamom_log_flux"] = np.log10(cat["adamom_flux"])
	cat["adamom_frac"] = np.sum(cat["adamom_g1"].mask, axis=1)/float(cat["adamom_g1"].shape[1])
	megalut.tools.table.addstats(cat, "adamom_flux")
	megalut.tools.table.addstats(cat, "adamom_sigma")
	megalut.tools.table.addstats(cat, "snr")
	snr_mean = Feature("snr_mean")

	
	#print min(cat["adamom_frac"]), max(cat["adamom_frac"]), np.median(cat["adamom_frac"])

	s = megalut.tools.table.Selector("ok", [
		("in", "snr_mean", 3, 15),
		("min", "tru_rad", 0.5),
		("in", "tru_rad", 0.5, 2.7),
		("max", "adamom_frac", 0.02)
		])

	cat = s.select(cat)

	#print min(cat["snr_mean"]), max(cat["snr_mean"]), np.median(cat["snr_mean"])
	
	
	if component == 1:
	
		cat["pre_g1"] = cat["pre_g1_adamom"]
		megalut.tools.table.addstats(cat, "pre_g1")
		megalut.tools.table.addrmsd(cat, "pre_g1", "tru_s1")
		pre_gc_bias = Feature("pre_g1_bias")
		pre_gc_mean = Feature("pre_g1_mean")
		tru_sc = Feature("tru_s1")

		
	elif component == 2:
		
		cat["pre_g2"] = cat["pre_g2_adamom"]
		megalut.tools.table.addstats(cat, "pre_g2")
		megalut.tools.table.addrmsd(cat, "pre_g2", "tru_s2")
		pre_gc_bias = Feature("pre_g2_bias")
		pre_gc_mean = Feature("pre_g2_mean")
		tru_sc = Feature("tru_s2")

	ebarmode = "scatter"

	fig = plt.figure(figsize=(24, 12))

	ax = fig.add_subplot(3, 5, 1)
	megalut.plot.scatter.scatter(ax, cat, tru_sc,  pre_gc_mean, featc=snr_mean, showidline=True, metrics=True)
	
	ax = fig.add_subplot(3, 5, 2)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, Feature("snr_mean"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 3)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, Feature("tru_rad"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 4)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, Feature("tru_sersicn"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 5)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, Feature("tru_g"), pre_gc_bias)

	
	ax = fig.add_subplot(3, 5, 6)
	megalut.plot.scatter.scatter(ax, cat, tru_sc,  Feature("tru_sb"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 7)
	megalut.plot.scatter.scatter(ax, cat, tru_sc,  Feature("adamom_frac"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 8)
	megalut.plot.scatter.scatter(ax, cat, tru_sc,  Feature("tru_flux"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 9)
	megalut.plot.scatter.scatter(ax, cat, tru_sc,  Feature("adamom_flux", rea=1), pre_gc_bias)
	#megalut.plot.scatter.scatter(ax, cat, tru_sc,  Feature("adamom_flux_mean"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 10)
	megalut.plot.scatter.scatter(ax, cat, tru_sc,  Feature("adamom_sigma", rea=1), pre_gc_bias)

	
	ax = fig.add_subplot(3, 5, 11)
	megalut.plot.bin.res(ax, cat, tru_sc, pre_gc_mean, Feature("tru_sb"), ncbins=3, equalcount=True, ebarmode=ebarmode)
	ax = fig.add_subplot(3, 5, 12)
	megalut.plot.bin.res(ax, cat, tru_sc, pre_gc_mean, Feature("tru_flux"), ncbins=3, equalcount=True, ebarmode=ebarmode)
	ax = fig.add_subplot(3, 5, 13)
	megalut.plot.bin.res(ax, cat, tru_sc, pre_gc_mean, Feature("tru_rad"), ncbins=3, equalcount=True, ebarmode=ebarmode)
	ax = fig.add_subplot(3, 5, 14)
	megalut.plot.bin.res(ax, cat, tru_sc, pre_gc_mean, Feature("tru_sersicn"), ncbins=3, equalcount=True, ebarmode=ebarmode)
	ax = fig.add_subplot(3, 5, 15)
	megalut.plot.bin.res(ax, cat, tru_sc, pre_gc_mean, Feature("tru_g"), ncbins=3, equalcount=True, ebarmode=ebarmode)

	
	
	
	plt.tight_layout()

	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.


if __name__ == "__main__":
    main()
	
