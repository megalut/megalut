"""
Validation plot on mixed-galaxies data, with optional weights
"""

import megalut
import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt
import numpy as np

import includes

import os

import logging
logger = logging.getLogger(__name__)



predname = "test1"

component = 2 # which component


def main():


	catpath = os.path.join(includes.workdir, "train_simple", "valprewcat.pkl")
	#catpath = config.great3.path("val","%03i" % subfield, "predcat_{}.pkl".format(predname))
	cat = megalut.tools.io.readpickle(catpath)
	print megalut.tools.table.info(cat)
		
	
	#print "HACK HACK HACK"	
	#cat["pre_s1w"] = np.asarray(cat["snr"] > 6, dtype=float)#np.logical_and(cat["snr"] > 6, cat["snr"] < 10), dtype=float)
	#cat["pre_s1w"] = np.asarray(cat["pre_s1w"] > 0.4, dtype=float)
	
	# Checking that the predictions are correctly masked:
	#assert np.sum(cat["adamom_g1"].mask) == np.sum(cat["pre_s1"].mask)
	#assert np.sum(cat["adamom_g1"].mask) == np.sum(cat["pre_s1w"].mask)
	
	#print megalut.tools.table.info(cat)
	#print cat["pre_s1", "snr", "pre_s1w"]
	#exit()
		
	
	plotpath = None
	#plotpath = config.great3.path("ml","%03i" % subfield, "valplot_{}_comp{}.png".format(predname, component))
	
	plot(cat, component, filepath=plotpath, title = predname)
	logger.info("Plotted to {}".format(plotpath))




def plot(cat, component, filepath=None, title=None):
	
	#rea = "all"
	rea = -20
	ebarmode = "scatter"
	
	if component == 1:
	
		# Adding weights if absent:
		if not "pre_s1w" in cat.colnames:
			cat["pre_s1w"] = np.ones(cat["adamom_g1"].shape)
	
		cat["pre_s1w_norm"] = cat["pre_s1w"] / np.max(cat["pre_s1w"])

		megalut.tools.table.addrmsd(cat, "pre_s1", "tru_s1")
		megalut.tools.table.addstats(cat, "pre_s1", "pre_s1w")
		cat["pre_s1_wbias"] = cat["pre_s1_wmean"] - cat["tru_s1"]
		
		pre_scw = Feature("pre_s1w", rea=rea)
		pre_scw_norm = Feature("pre_s1w_norm", rea=rea)
		
		pre_sc = Feature("pre_s1", rea=rea)
		
		pre_sc_bias = Feature("pre_s1_bias")
		pre_sc_wbias = Feature("pre_s1_wbias")
		
		pre_sc_mean = Feature("pre_s1_mean", -0.13, 0.13)
		pre_sc_wmean = Feature("pre_s1_wmean", -0.13, 0.13)
		
		tru_sc = Feature("tru_s1", -0.13, 0.13)
		
		
	elif component == 2:
		# Adding weights if absent:
		if not "pre_s2w" in cat.colnames:
			cat["pre_s2w"] = np.ones(cat["adamom_g2"].shape)
	
		cat["pre_s2w_norm"] = cat["pre_s2w"] / np.max(cat["pre_s2w"])

		megalut.tools.table.addrmsd(cat, "pre_s2", "tru_s2")
		megalut.tools.table.addstats(cat, "pre_s2", "pre_s2w")
		cat["pre_s2_wbias"] = cat["pre_s2_wmean"] - cat["tru_s2"]
		
		pre_scw = Feature("pre_s2w", rea=rea)
		pre_scw_norm = Feature("pre_s2w_norm", rea=rea)
		
		pre_sc = Feature("pre_s2", rea=rea)
		
		pre_sc_bias = Feature("pre_s2_bias")
		pre_sc_wbias = Feature("pre_s2_wbias")
		
		pre_sc_mean = Feature("pre_s2_mean", -0.13, 0.13)
		pre_sc_wmean = Feature("pre_s2_wmean", -0.13, 0.13)
		
		tru_sc = Feature("tru_s2", -0.13, 0.13)
		


	fig = plt.figure(figsize=(20, 12))
	if title is not None:
		fig.suptitle(title)

	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, pre_sc, pre_scw)
	
	ax = fig.add_subplot(3, 4, 3)
	megalut.plot.scatter.scatter(ax, cat, Feature("tru_rad", rea=rea), Feature("adamom_sigma", rea=rea), featc=pre_scw)
	
	ax = fig.add_subplot(3, 4, 4)
	megalut.plot.scatter.scatter(ax, cat, Feature("adamom_flux", rea=rea), Feature("tru_flux", rea=rea), featc=pre_scw)
	
	ax = fig.add_subplot(3, 4, 5)
	megalut.plot.scatter.scatter(ax, cat, Feature("snr", rea=rea), pre_scw)
	
	ax = fig.add_subplot(3, 4, 6)
	megalut.plot.hist.hist(ax, cat, pre_scw)

	ax = fig.add_subplot(3, 4, 7)
	megalut.plot.scatter.scatter(ax, cat, Feature("adamom_sigma", rea=rea), Feature("adamom_flux", rea=rea), featc=pre_scw)
	
	ax = fig.add_subplot(3, 4, 8)
	megalut.plot.scatter.scatter(ax, cat, Feature("tru_rad", rea=rea), Feature("tru_flux", rea=rea), featc=pre_scw)



	ax = fig.add_subplot(3, 4, 9)
	megalut.plot.bin.bin(ax, cat, tru_sc, pre_sc_bias, showidline=True,  metrics=True, yisres=True)
	ax.set_title("Without weights")

	ax = fig.add_subplot(3, 4, 10)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, pre_sc_bias, showidline=True, metrics=True, yisres=True)
	ax.set_title("Without weights")
	
	ax = fig.add_subplot(3, 4, 11)
	megalut.plot.bin.bin(ax, cat, tru_sc, pre_sc_wbias, showidline=True, metrics=True, yisres=True)
	ax.set_title("With weights")

	ax = fig.add_subplot(3, 4, 12)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, pre_sc_wbias, showidline=True, metrics=True, yisres=True)
	ax.set_title("With weights")

	
	plt.tight_layout()

	if filepath:
		logger.info("Writing plot to '{}'...".format(filepath))
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.


if __name__ == "__main__":
	main()
	
