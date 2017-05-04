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

redo = True

def main():
	
	
	sheartraindir = os.path.join(config.traindir, config.datasets["train-shear"])
	weighttraindir = os.path.join(config.traindir, config.datasets["train-weight"])

	valname = "pred_{}".format(config.datasets["valid-shear"])
	predcatpath = os.path.join(config.valdir, valname + ".pkl")

	catpath = os.path.join(config.simmeasdir, config.datasets["valid-shear"], "groupmeascat.pkl")
	
	
	if (redo is True) or (not os.path.exists(predcatpath)):
		cat = megalut.tools.io.readpickle(catpath)
		#print megalut.tools.table.info(cat)
	
		cat = megalut.learn.tenbilacrun.predict(cat, config.shearconflist , sheartraindir)
		if len(config.weightconflist) > 0:
			cat = megalut.learn.tenbilacrun.predict(cat, config.weightconflist , weighttraindir)
	
	
		megalut.tools.io.writepickle(cat, predcatpath)
	
	else:
		logger.info("Reusing existing preds")
		cat = megalut.tools.io.readpickle(predcatpath)
		print megalut.tools.table.info(cat)
	

	cat = cat[cat["magnitude"] < 24.0]
	plot(cat, component=1)





		
def plot(cat, component, filepath=None, title=None):
	
	#rea = "all"
	rea = -20
	ebarmode = "scatter"
	srad = 0.07
	sbrad = 0.02
	
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
	
	pre_sc_mean = Feature("pre_s{}_mean".format(component), -sbrad, sbrad)
	pre_sc_wmean = Feature("pre_s{}_wmean".format(component), -srad, srad)
	
	tru_sc = Feature("tru_s{}".format(component), -srad, srad)
		
	cat["tru_bulge_fraction"] = cat["tru_bulge_flux"] / (cat["tru_bulge_flux"] + cat["tru_disk_flux"])


	fig = plt.figure(figsize=(20, 12))
	if title is not None:
		fig.suptitle(title)

	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, pre_sc, pre_scw)
	

	ax = fig.add_subplot(3, 4, 5)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, Feature("magnitude"), pre_sc_bias)
	ax = fig.add_subplot(3, 4, 6)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, Feature("tru_bulge_g"), pre_sc_bias)
	ax = fig.add_subplot(3, 4, 7)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, Feature("tru_bulge_fraction"), pre_sc_bias)
	ax = fig.add_subplot(3, 4, 8)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, Feature("hlr_disk_arcsec"), pre_sc_bias)
	

	ax = fig.add_subplot(3, 4, 9)
	megalut.plot.bin.res(ax, cat, tru_sc, pre_sc_mean, Feature("magnitude"), ncbins=3, equalcount=True, ebarmode=ebarmode)
	ax = fig.add_subplot(3, 4, 10)
	megalut.plot.bin.res(ax, cat, tru_sc, pre_sc_mean, Feature("tru_bulge_g"), ncbins=3, equalcount=True, ebarmode=ebarmode)
	ax = fig.add_subplot(3, 4, 11)
	megalut.plot.bin.res(ax, cat, tru_sc, pre_sc_mean, Feature("tru_bulge_fraction"), ncbins=3, equalcount=True, ebarmode=ebarmode)
	ax = fig.add_subplot(3, 4, 12)
	megalut.plot.bin.res(ax, cat, tru_sc, pre_sc_mean, Feature("hlr_disk_arcsec"), ncbins=3, equalcount=True, ebarmode=ebarmode)


	
	plt.tight_layout()

	if filepath:
		logger.info("Writing plot to '{}'...".format(filepath))
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.



if __name__ == "__main__":
    main()
