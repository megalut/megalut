import megalut.tools
import megalut.learn
import megalut
import astropy

import config
import numpy as np
import os
import glob

from megalut.tools.feature import Feature
import matplotlib.pyplot as plt
import megalut.plot

import run_51_val

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

import SHE_GSM_BiasMeasurement.bias_calculation

def main():

	
	meascatpath = os.path.join(config.obsproddir, "meascat.pkl")
	predcatpath = os.path.join(config.obsproddir, "predmeascat.pkl")

	# Reading in the observations
	"""
	catpaths = sorted(glob.glob(os.path.join(config.obsproddir, "*/meascat_*.pkl")))
	assert len(catpaths) == 100

	cats = [megalut.tools.io.readpickle(catpath) for catpath in catpaths]
	cat = astropy.table.vstack(cats, join_type="exact")

	print megalut.tools.table.info(cat)

	megalut.tools.io.writepickle(cat, meascatpath)
	

	# Computing the true shear
	
	cat = megalut.tools.io.readpickle(meascatpath)

	cat["tru_s1"] = cat["shear_magnitude"] * np.cos(2.0 * cat["shear_angle"] * np.pi/180.0)
	cat["tru_s2"] = cat["shear_magnitude"] * np.sin(2.0 * cat["shear_angle"] * np.pi/180.0)
	

	# Predicting				
	sheartraindir = os.path.join(config.traindir, config.datasets["train-shear"])
	weighttraindir = os.path.join(config.traindir, config.datasets["train-weight"])

	cat = megalut.learn.tenbilacrun.predict(cat, config.shearconflist , sheartraindir)
	if len(config.weightconflist) > 0:
		cat = megalut.learn.tenbilacrun.predict(cat, config.weightconflist , weighttraindir)
	
	
	megalut.tools.io.writepickle(cat, predcatpath)
	"""
	
	
	cat = megalut.tools.io.readpickle(predcatpath)

	
	# Testing Bryan's code: YES, it gives the same as wmetrics
	"""
	# This is for not-yet-group-shaped data:
	
	for component in [1, 2]:
		pre_scw = Feature("pre_s{}w".format(component))
		pre_sc = Feature("pre_s{}".format(component))
		tru_sc = Feature("tru_s{}".format(component))
	
		#print megalut.tools.metrics.metrics(cat, tru_sc, pre_sc, pre_is_res=False)
		#print megalut.tools.metrics.wmetrics(cat, tru_sc, pre_sc, pre_scw)
	
		metcat = megalut.tools.feature.get1Ddata(cat, [tru_sc, pre_sc, pre_scw], keepmasked=False)
		x = metcat[tru_sc.colname]
		y = metcat[pre_sc.colname]
		w = metcat[pre_scw.colname]
		yerr = 1./np.sqrt(w)
		#yerr = np.ones(len(x))

		ret = SHE_GSM_BiasMeasurement.bias_calculation.regress_shear_measurements(x, y, yerr)
		(m, merr, c, cerr, mc_covar) = ret
	
		txt = "m*1e3: %.1f +/- %.1f   c*1e3: %.1f +/- %.1f" % (m*1000.0, merr*1000.0, c*1000.0, cerr*1000.0)
		logger.info("Regression: {}".format(txt))	
	
	
	exit()
	"""
	
	cat = megalut.tools.table.fastgroupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])
	#cat = megalut.tools.io.readpickle("/vol/fohlen11/fohlen11_1/mtewes/Euclid/senstest/megalut/val/pred_tw-1-sheargroup4-large.pkl")
	
	print megalut.tools.table.info(cat)

	
	for component in [1,2]:
		
		megalut.tools.table.addstats(cat, "pre_s{}".format(component), "pre_s{}w".format(component))

		srad = 0.07
		pre_sc_mean = Feature("pre_s{}_mean".format(component), -srad, srad)
		pre_sc_wmean = Feature("pre_s{}_wmean".format(component), -srad, srad)
		pre_sc_wmeanw = Feature("pre_s{}_wmeanw".format(component))
		
		
		megalut.tools.metrics.wmetrics(cat, Feature("tru_s{}".format(component)), Feature("pre_s{}_wmean".format(component)), wfeat=Feature("pre_s{}_wmeanw".format(component)))
	
		
		"""
		tru_sc = Feature("tru_s{}".format(component), -srad, srad)

		fig = plt.figure(figsize=(20, 12))

		ax = fig.add_subplot(3, 4, 1)
		megalut.plot.scatter.scatter(ax, cat, tru_sc, pre_sc_mean, metrics=True)
	
		ax = fig.add_subplot(3, 4, 2)
		megalut.plot.scatter.scatter(ax, cat, tru_sc, pre_sc_wmean, metrics=True)

		ax = fig.add_subplot(3, 4, 3)
		megalut.plot.hist.hist(ax, cat, pre_sc_wmeanw)

		plt.tight_layout()
	
		plt.show()
		plt.close(fig) # Helps releasing memory when calling in large loops.

		exit()
		"""
	
	
	
	
	#plot(cat, component=1)
	
	#run_51_val.plot(cat, component=1)


def plot(cat, component):
	
	rea = "all"
	ebarmode = "scatter"
	srad = 0.07

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

	ax = fig.add_subplot(3, 4, 1)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, pre_sc_mean, metrics=True)
	
	ax = fig.add_subplot(3, 4, 2)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, pre_sc_wmean, metrics=True)

	plt.tight_layout()

	plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.



if __name__ == "__main__":
    main()
