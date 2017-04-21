import megalut.tools
import megalut.learn
import megalut

import config
import numpy as np
import os

from megalut.tools.feature import Feature
import matplotlib.pyplot as plt
import megalut.plot


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
	
	measdir = os.path.join(config.simmeasdir, config.datasets["train-shear"])
	sheartraindir = os.path.join(config.traindir, config.datasets["train-shear"])
	weighttraindir = os.path.join(config.traindir, config.datasets["train-weight"])

	valname = "pred_{}".format(config.datasets["valid-overall"]) # Too messy to add everything here.
	predcatpath = os.path.join(config.valdir, valname + ".pkl")

	catpath = os.path.join(config.simmeasdir, config.datasets["valid-overall"], "groupmeascat.pkl")
	cat = megalut.tools.io.readpickle(catpath)
	#print megalut.tools.table.info(cat)
	
	cat = megalut.learn.tenbilacrun.predict(cat, config.shearconflist , sheartraindir)
	if len(config.weightconflist) > 0:
		cat = megalut.learn.tenbilacrun.predict(cat, config.weightconflist , weighttraindir)
	
	
	megalut.tools.io.writepickle(cat, predcatpath)

	plot(cat, component=1)





		
def plot(cat, component, filepath=None, title=None):
	
	#rea = "all"
	rea = -20
	ebarmode = "scatter"
	srad = 0.07
	
	# Adding weights if absent:
	if not "pre_s{}w".format(component) in cat.colnames:
		
		# First putting all weights to 1.0:
		cat["pre_s{}w".format(component)] = np.ones(cat["adamom_g1"].shape)
		
		
		# Keeping only the best half of SNR
		megalut.tools.table.addstats(cat, "snr")
		for row in cat:
			row["pre_s{}w".format(component)] = np.array(row["snr"] > row["snr_med"], dtype=np.float)
		
		"""
		# Keeping the best half of sigma
		megalut.tools.table.addstats(cat, "adamom_sigma")
		for row in cat:
			row["pre_s{}w".format(component)] = np.array(row["adamom_sigma"] > row["adamom_sigma_med"], dtype=np.float)
		"""
		
		
		#print megalut.tools.table.info(cat)
		
		cat["pre_s{}w_norm".format(component)] = cat["pre_s{}w".format(component)] / np.max(cat["pre_s{}w".format(component)])
	
	megalut.tools.table.addrmsd(cat, "pre_s{}".format(component), "tru_s{}".format(component))

	megalut.tools.table.addstats(cat, "pre_s{}".format(component), "pre_s{}w".format(component))
	cat["pre_s{}_wbias".format(component)] = cat["pre_s{}_wmean".format(component)] - cat["tru_s{}".format(component)]
	
	pre_scw = Feature("pre_s{}w".format(component), rea=rea)
	pre_scw_norm = Feature("pre_s{}w_norm".format(component), rea=rea)
	
	pre_sc = Feature("pre_s{}".format(component), rea=rea)
	
	pre_sc_bias = Feature("pre_s{}_bias".format(component))
	pre_sc_wbias = Feature("pre_s{}_wbias".format(component))
	
	pre_sc_mean = Feature("pre_s{}_mean".format(component), -srad, srad)
	pre_sc_wmean = Feature("pre_s{}_wmean".format(component), -srad, srad)
	
	tru_sc = Feature("tru_s{}".format(component), -srad, srad)
		


	fig = plt.figure(figsize=(20, 12))
	if title is not None:
		fig.suptitle(title)

	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, pre_sc, pre_scw)
	
	"""
	ax = fig.add_subplot(3, 4, 5)
	if component ==1:
		theother=Feature("tru_g2", rea=rea)
	else:
		theother=Feature("tru_g1", rea=rea)
	megalut.plot.scatter.scatter(ax, cat, Feature("snr", rea=rea), pre_scw, theother)
	
	"""
	ax = fig.add_subplot(3, 4, 6)
	megalut.plot.hist.hist(ax, cat, pre_scw)

	ax = fig.add_subplot(3, 4, 7)
	megalut.plot.scatter.scatter(ax, cat, Feature("adamom_sigma", rea=rea), Feature("adamom_flux", rea=rea), featc=pre_scw)
	
	
	nbins=5
	
	ax = fig.add_subplot(3, 4, 9)
	megalut.plot.bin.bin(ax, cat, tru_sc, pre_sc_bias, showidline=True,  metrics=True, yisres=True, nbins=nbins)
	ax.set_title("Without weights")

	ax = fig.add_subplot(3, 4, 10)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, pre_sc_bias, showidline=True, metrics=True, yisres=True)
	ax.set_title("Without weights")
	
	ax = fig.add_subplot(3, 4, 11)
	megalut.plot.bin.bin(ax, cat, tru_sc, pre_sc_wbias, showidline=True, metrics=True, yisres=True, nbins=nbins)
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
