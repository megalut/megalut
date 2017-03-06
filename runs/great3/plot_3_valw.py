"""
Validation plot on mixed-galaxies data, with optional weights
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



#predname = "test1"

#component = 1 # which component


def main():


	for subfield in config.great3.subfields:
		
		# Would need to be updated
		"""
		catpath = "/vol/fohlen11/fohlen11_1/mtewes/2017_MegaLUT_GREAT3/cgc_v1/ml/099/G3CGCSersics_train_nn/predcat_ada4_sum55_statshear.pkl"
		#catpath = config.great3.path("val","%03i" % subfield, "predcat_{}.pkl".format(predname))
		cat = megalut.tools.io.readpickle(catpath)
		#print megalut.tools.table.info(cat)
			
		
		#print "HACK HACK HACK"	
		cat["pre_s1w"] = np.asarray(cat["snr"] > 5, dtype=float)
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
		"""



def plot(cat, component, filepath=None, title=None):
	
	#rea = "all"
	rea = -20
	ebarmode = "scatter"
	

	
	# Adding weights if absent:
	if not "pre_s{}w".format(component) in cat.colnames:
		cat["pre_s{}w".format(component)] = np.ones(cat["adamom_g1"].shape)
		cat["pre_s{}w_norm".format(component)] = cat["pre_s{}w".format(component)] / np.max(cat["pre_s{}w".format(component)])
	
	megalut.tools.table.addrmsd(cat, "pre_s{}".format(component), "tru_s{}".format(component))

	megalut.tools.table.addstats(cat, "pre_s{}".format(component), "pre_s{}w".format(component))
	cat["pre_s{}_wbias".format(component)] = cat["pre_s{}_wmean".format(component)] - cat["tru_s{}".format(component)]
	
	pre_scw = Feature("pre_s{}w".format(component), rea=rea)
	pre_scw_norm = Feature("pre_s{}w_norm".format(component), rea=rea)
	
	pre_sc = Feature("pre_s{}".format(component), rea=rea)
	
	pre_sc_bias = Feature("pre_s{}_bias".format(component))
	pre_sc_wbias = Feature("pre_s{}_wbias".format(component))
	
	pre_sc_mean = Feature("pre_s{}_mean".format(component), -0.13, 0.13)
	pre_sc_wmean = Feature("pre_s{}_wmean".format(component), -0.13, 0.13)
	
	tru_sc = Feature("tru_s{}".format(component), -0.13, 0.13)
		


	fig = plt.figure(figsize=(20, 12))
	if title is not None:
		fig.suptitle(title)

	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, pre_sc, pre_scw)
	
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
	
